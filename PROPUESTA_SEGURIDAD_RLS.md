# Propuesta de seguridad RLS: borrador no ejecutado

21 de octubre de 2026. Alcance aclarado por el usuario: solicitudes en móvil; consulta/seguimiento en web. Tipos web nuevos autorizados en código local: admin_psicologia y admin_dentista. No se crearon cuentas ni se concedieron privilegios en producción.

## Hallazgos

La auditoría verificó en el panel del proyecto `ctiqbycbkcftwuqgzxjb` RLS activo en ambas tablas clínicas, SELECT e INSERT permisivos a PUBLIC con condiciones true y grants excesivos a anon/authenticated, incluyendo TRUNCATE. No hay políticas UPDATE/DELETE. Las tablas tienen FK de paciente/profesional a perfiles; borrar el perfil del paciente elimina sus atenciones en cascada y borrar el profesional deja NULL. perfiles depende de auth.users con cascada. Sólo existen índices de PK y no hay CHECK de costo/sesión.

En perfiles se observó RLS desactivado. El backend nuevo verifica token con Auth y rol desde perfiles, pero esa fuente debe estar protegida también contra elevación por la Data API. Se añadió un guard en Gestión de Usuarios y se retiró el fallback a user_metadata de la autorización para registrar usuarios; eso no demuestra que todos los canales productivos estén cerrados. Los backends antiguos de Traslados/Comidas conservan reglas propias y requieren una auditoría independiente antes de afirmar aislamiento total del sistema.

## Modelo recomendado

| Rol | Psicología web | Dentista web |
|---|---|---|
| admin | Consulta y seguimiento aprobado | Consulta y seguimiento aprobado |
| admin_psicologia | Consulta y seguimiento aprobado | Denegado |
| admin_dentista | Denegado | Consulta y seguimiento aprobado |
| otros/anon | Denegado | Denegado |

Cada responsable consulta los registros visibles de su área. Asignación individual por profesional no está acordada. No conceder acceso clínico por UUID de paciente/profesional sin una regla explícita.

Proteger el origen del rol: se propone combinar perfil consistente con un claim firmado `app_metadata.role`, provisionado sólo por un proceso de administración confiable. No usar user_metadata ni rol de headers. Es una propuesta, no se presume que las cuentas existentes tengan ese claim. Antes de aplicarla deben aprobarse y validarse aprovisionamiento, cambio/revocación de rol, expiración/refresh de JWT y alineación del backend. Mientras tanto, la implementación local consulta perfiles y depende de su integridad.

Las altas de cuentas siguen el servicio Auth administrativo existente de FORMADIG; no trasladar esa clave a los servicios clínicos. El login continúa siendo único. No escribir secretos en el repositorio. No usar service_role para superar la falta de políticas de seguimiento.

## Borrador SQL para ensayo en desarrollo

NO ejecutar en producción. Antes de aplicar: inventariar todas las políticas, ACL, claims, configuración de Data API y comportamiento de la app móvil. Las políticas permisivas se combinan con OR: una política pública restante invalidaría la restricción. La política de INSERT móvil debe diseñarse y probarse primero; quitar la política pública sin reemplazo impediría las solicitudes móviles. El SQL siguiente muestra el acceso web, no implementa ese contrato móvil pendiente.

```sql
BEGIN;
ALTER TABLE public.modulo_dental ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.modulo_psicologia ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.modulo_dental, public.modulo_psicologia FROM PUBLIC, anon, authenticated;
GRANT SELECT ON public.modulo_dental, public.modulo_psicologia TO authenticated;

DROP POLICY IF EXISTS "Lectura publica modulo_dental" ON public.modulo_dental;
DROP POLICY IF EXISTS "Lectura publica modulo_psicologia" ON public.modulo_psicologia;
-- Sustituir INSERT público sólo al tener la política móvil aprobada y ensayada.
DROP POLICY IF EXISTS "Insercion modulo_dental" ON public.modulo_dental;
DROP POLICY IF EXISTS "Insercion modulo_psicologia" ON public.modulo_psicologia;

CREATE POLICY dental_web_select ON public.modulo_dental
FOR SELECT TO authenticated USING (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_dentista')
  AND EXISTS (SELECT 1 FROM public.perfiles p
    WHERE p.id=(SELECT auth.uid())
      AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
);
CREATE POLICY psicologia_web_select ON public.modulo_psicologia
FOR SELECT TO authenticated USING (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_psicologia')
  AND EXISTS (SELECT 1 FROM public.perfiles p
    WHERE p.id=(SELECT auth.uid())
      AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
);
COMMIT;
```

El EXISTS exige lectura segura del propio perfil. El join de nombres de paciente necesita una política de lectura mínima de perfiles para el responsable autorizado, sin conceder por ello acceso general a CURP/domicilio/teléfono o permiso para cambiar roles. Diseñar esa exposición por columnas o un recurso dedicado según el contrato móvil, fuera de esta fase. No agregar SECURITY DEFINER ni desactivar RLS para resolver recursión/permisos.

### Segunda etapa: seguimiento web aprobado

No aplicar automáticamente ni habilitar CLINICAL_ENABLE_UPDATES antes de validar.

```sql
GRANT UPDATE (motivo_consulta, diagnostico, tratamiento_realizado,
              costo_recuperacion, fecha_atencion)
ON public.modulo_dental TO authenticated;
CREATE POLICY dental_web_update ON public.modulo_dental
FOR UPDATE TO authenticated
USING (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_dentista')
  AND EXISTS (SELECT 1 FROM public.perfiles p WHERE p.id=(SELECT auth.uid())
    AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
) WITH CHECK (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_dentista')
  AND EXISTS (SELECT 1 FROM public.perfiles p WHERE p.id=(SELECT auth.uid())
    AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
);

GRANT UPDATE (tipo_atencion, motivo_consulta, diagnostico_inicial,
              numero_sesion, estatus_caso, fecha_sesion)
ON public.modulo_psicologia TO authenticated;
CREATE POLICY psicologia_web_update ON public.modulo_psicologia
FOR UPDATE TO authenticated
USING (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_psicologia')
  AND EXISTS (SELECT 1 FROM public.perfiles p WHERE p.id=(SELECT auth.uid())
    AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
) WITH CHECK (
  (SELECT auth.jwt()->'app_metadata'->>'role') IN ('admin','admin_psicologia')
  AND EXISTS (SELECT 1 FROM public.perfiles p WHERE p.id=(SELECT auth.uid())
    AND p.rol=(SELECT auth.jwt()->'app_metadata'->>'role'))
);
```

SELECT es necesario para UPDATE. Grants por columna impiden reasignar paciente, profesional o ID desde la Data API. No conceder DELETE/TRUNCATE al flujo clínico. Definir conservación de expedientes y auditoría antes de tocar las bajas de perfiles/Auth. No hay control de versiones concurrentes ni trazabilidad de cambios en el esquema auditado; aprobar esas necesidades antes de uso clínico real.

### Índices/validaciones para evaluar

```sql
-- Propuestas, no ejecutadas. Evaluar planes de consulta y datos previos.
CREATE INDEX modulo_dental_paciente_fecha_idx
 ON public.modulo_dental (paciente_id, fecha_atencion DESC, id DESC);
CREATE INDEX modulo_psicologia_paciente_fecha_idx
 ON public.modulo_psicologia (paciente_id, fecha_sesion DESC, id DESC);
ALTER TABLE public.modulo_dental ADD CONSTRAINT dental_costo_no_negativo
 CHECK (costo_recuperacion IS NULL OR costo_recuperacion >= 0) NOT VALID;
ALTER TABLE public.modulo_psicologia ADD CONSTRAINT psicologia_sesion_positiva
 CHECK (numero_sesion IS NULL OR numero_sesion >= 1) NOT VALID;
```

No cambiar CASCADE, agregar columnas de estatus dental o catálogos sin acuerdo de negocio y revisión de dependencias móviles. Crear una migración real con el flujo de Supabase CLI sólo después de aprobación; este documento no escribe historial de migraciones.

## Pruebas positivas/negativas y plan

1. Preparar una base de desarrollo con esquema y cuentas/datos sintéticos, sin copiar pacientes productivos. Capturar esquema/políticas/ACL para rollback revisado.
2. Aprovisionar cinco tipos web sintéticos y un paciente móvil. Verificar fuente confiable del rol, políticas de perfiles, exposición Data API, grants de esquema y ausencia de políticas públicas residuales.
3. Positivas: admin consulta ambas áreas; cada responsable consulta sólo su área; cada uno actualiza seguimiento sólo después de aprobar UPDATE; móvil registra solicitud mediante su contrato aprobado.
4. Negativas: anon, JWT inválido/vencido/otro proyecto, Desayunos y Traslados sin acceso clínico; Psicología denegado en Dentista y viceversa; localStorage, headers y user_metadata falsos no elevan permisos. Probar REST directo además de Flask.
5. Rechazar reasignación de paciente/profesional/ID, campos inválidos, DELETE y TRUNCATE. Cero filas por RLS no debe parecer una edición exitosa. Probar join de nombre del paciente sin exponer otros campos.
6. Probar cambio/revocación de roles y refresh. Revisar regresiones en login, administración de usuarios, móvil, Traslados, Comidas y Chatbot. Ejecutar advisors en desarrollo.
7. Revisar resultados y SQL/rollback antes de aprobar despliegue o cambios productivos. La bandera de seguimiento no concede permisos en PostgreSQL.

Ahora se ejecutaron mocks/fakes y pruebas de interfaz local; no prueban políticas reales de PostgreSQL. La verificación RLS de desarrollo sigue pendiente.

Referencias: [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Seguridad Data API](https://supabase.com/docs/guides/api/securing-your-api).
