# FORMADIG — Activación Supabase real

23 de octubre de 2026. Proyecto autorizado: DIF (`ctiqbycbkcftwuqgzxjb`). Estado: **contención clínica aplicada; cuentas reales y despliegue pendientes por acceso técnico**.

## 1. Operaciones realmente efectuadas en Supabase

El conector MCP denegó `get_project`, SELECT de metadatos y `apply_migration` con «You do not have permission to perform this action». No se usó otro proyecto. La sesión autenticada de Chrome sí mostró DIF/main PRODUCTION y permitió usar SQL Editor.

Se inspeccionaron políticas, grants de tabla y columna, trigger Auth y dependencias clínicas mediante SELECT de metadatos. Antes de intervenir seguían las cuatro políticas clínicas públicas SELECT/INSERT true, grants amplios, perfiles sin RLS y `handle_new_user()` tomando `raw_user_meta_data.rol`. No se consultaron expedientes. La consulta de esquemas no encontró `formadig_private` ni `supabase_migrations`; no se considera confirmado ningún historial remoto de las migraciones propuestas.

Se ejecutó y confirmó COMMIT de una transacción de contención clínica en SQL Editor: RLS habilitado, REVOKE ALL sobre ambas tablas para PUBLIC/anon/authenticated y política `clinical_containment` RESTRICTIVE FOR ALL USING(false) WITH CHECK(false) en cada tabla. Incluyó preflight de cuatro políticas y ausencia de ACL de columna, y lock_timeout de 5 segundos. No cambió filas, perfiles, identidades ni roles existentes.

El delta está versionado en `supabase/migrations/20261023214516_formadig_clinical_containment.sql`, generado con Supabase CLI 2.122.0. **Se aplicó por SQL Editor como contención urgente, no por el servicio de migraciones; no quedó registrado en su historial.** Antes de cualquier db push hay que conciliar este cambio y el orden de ejecución mediante el mecanismo oficial. No repetir CREATE POLICY ni marcar como aplicadas las fases A/B que no se ejecutaron.

## 2. Estado RLS y grants resultantes

En `modulo_psicologia` y `modulo_dental`, `relrowsecurity=true`. `has_table_privilege` devolvió false para SELECT de anon y para SELECT/INSERT/UPDATE/DELETE de authenticated en ambas tablas. Los grants amplios de postgres/service_role no se tocaron; no se usó service_role para consultar tablas. Las políticas públicas antiguas permanecen pero ya no conceden acceso efectivo a estos clientes: no tienen privilegios y existe una política restrictiva false.

Dos solicitudes REST reales con clave pública, `select=id&limit=0`, devolvieron HTTP 401 para ambas tablas. No devolvieron expedientes. Esto acredita denegación anónima, no login ni permisos positivos con JWT de profesionales. Las áreas clínicas quedan temporalmente cerradas incluso para personal web; no se presentará esa denegación como un módulo activado.

`public.perfiles` y su trigger heredado **siguen pendientes de corrección**. No se declara segura toda la base ni se certifican funciones privilegiadas o consumidores ajenos al alcance.

## 3. Trigger y registro protegido

Fase A `20261023202836_formadig_roles_protegidos.sql`: no aplicada. El registro privado todavía no existe. Sigue pendiente contrastar restricciones completas de perfiles y dependencias del trigger, aplicar mediante migraciones y verificar. No se migraron roles históricos automáticamente.

Fase B `20261023202914_formadig_rls_corte_coordinado.sql`: no aplicada. Se adaptó localmente para retirar la contención sólo durante el corte aprobado, verificar las dos políticas restrictivas adicionales y limitar lectura clínica a `atendido_por=auth.uid()` además del rol de área. Incluso admin requiere asignación por registro; no recibe acceso general a expedientes. Filas sin responsable no quedan visibles. No se asignaron registros reales a nadie. Las escrituras clínicas siguen prohibidas.

## 4. Tres cuentas solicitadas

El titular proporcionó y autorizó tres buzones controlados para admin, psicologo y dentista. Un SELECT filtrado exclusivamente por esos tres correos devolvió cero filas en Auth. No se enumeraron cuentas personales ajenas. No se crearon cuentas ni contraseñas reales: falta el acceso administrativo y resolver el trigger/perfiles antes de provisionar. Los identificadores demo .invalid anteriores no son cuentas Supabase.

Los correos autorizados se conservan en la conversación privada del titular; no se copian al repositorio. Las contraseñas futuras se entregarán fuera de Git en una salida local privada distinta de la demo, bajo LOCALAPPDATA/FORMADIG. Hoy no hay archivo de contraseñas reales creado por esta intervención.

## 5. Login y accesos reales

Sin cuentas creadas ni sesión autorizada no se probaron login, dashboard, navegación, coincidencia Auth/perfil/registro, denegación por rol, edición del rol ni logout con Supabase Auth real. No se sustituyen estos resultados por mocks. Sólo se verificó la denegación REST anónima y los privilegios efectivos PostgreSQL indicados.

## 6. Pruebas locales

- 47 pruebas Python aprobadas.
- 12 pruebas Node aprobadas.
- 96 comprobaciones PostgreSQL aisladas aprobadas, incluyendo contención anónima/autenticada y lectura por asignación. Auth/JWT son sintéticos en este laboratorio.
- Evidencia: `output/activation-containment-rls.json`. Los registros de las suites quedan locales, sin credenciales.

No se cambió HTML/CSS ni código móvil. Se conservaron las capturas, archivos ignorados, .env y evidencias previas. Los archivos históricos de metadatos no equivalen a un respaldo íntegro recuperable de producción; no se creó ni se afirma disponer de uno nuevo.

## 7. Compatibilidad y Render

No hubo push, merge a main ni modificación de Render. La comprobación HTTP de `/health` agotó el timeout de 40 segundos; `/api/status` no llegó a ejecutarse en ese intento. No se atribuye el timeout a la contención ni se afirma que el servicio esté caído. No se verificó una nueva revisión desplegada ni compatibilidad funcional con sesiones reales.

La Fase B mantiene su bloqueo de cuentas web históricas sin conciliación y exige aprobación del corte por conexión. La autorización de esta intervención no convierte automáticamente sus roles. La regresión real de Traslados/Desayunos/Gestión de Usuarios y el aprovisionamiento revisado siguen siendo controles previos al despliegue.

## 8. Bloqueos técnicos y continuación

Hace falta conectar MCP/CLI con una cuenta que tenga permisos reales sobre DIF para usar el mecanismo oficial de migraciones. Además, `SUPABASE_SERVICE_ROLE_KEY` no está configurada en el .env local ignorado: se necesita únicamente para Auth Admin, nunca para evadir RLS de tablas. No enviar esa clave al chat. Se solicitó al titular resolver estos accesos técnicos, sin volver a pedir autorización genérica.

Después: conciliar la contención con el historial oficial; completar preflight y respaldo de esquema recuperable; aplicar A; crear/verificar exactamente las tres cuentas por Auth Admin; comprobar registro y perfil; conciliar cuentas web anteriores explícitamente; ensayar y realizar corte B/backend; validar JWT/PostgREST reales con registros ficticios autorizados y negativos sin leer información clínica; comprobar Render y sólo entonces entregar credenciales operativas. No ejecutar db push indiscriminadamente: la Fase B no está lista para aplicarse automáticamente antes de la conciliación.

## 9. Restricciones que continúan

Creación, edición y eliminación clínica deshabilitadas. Sin cambios móviles ni afirmación de compatibilidad móvil. Sin SMS reales, bajas de usuarios, restauraciones, exportaciones personales ni cambios de roles ajenos. Las tres cuentas reales todavía **no están activadas**; la autorización está recibida, el acceso técnico sigue pendiente.
