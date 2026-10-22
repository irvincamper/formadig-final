# FORMADIG — controles RLS para DIF académico

21 de octubre de 2026. Proyecto autorizado: `ctiqbycbkcftwuqgzxjb`. **No aplicado. Intervención detenida por compatibilidad, según la instrucción expresa del titular.**

Esta revisión sustituye el borrador que exigía otro proyecto y revocaba indiscriminadamente accesos a perfiles. No ejecutar ese borrador sobre la base compartida. La autorización académica no elimina los controles de integridad ni exige una certificación empresarial.

## Evidencia actual

Inspección nueva mediante navegador: clínicas vacías con RLS activo, políticas públicas SELECT/INSERT; perfiles sin RLS con grants amplios. Trigger Auth SECURITY DEFINER copia rol de raw_user_meta_data. Exportación técnica en evidencias_supabase/20261021_seguridad_previa.json; procedimiento de reversión y límites en evidencias_supabase/PROCEDIMIENTO_REVERSION.md. No se han cambiado políticas, ACL, funciones ni datos.

## Requisitos funcionales de seguridad

| Identidad | Psicología | Dental | Perfiles/roles |
|---|---|---|---|
| admin | SELECT y seguimiento autorizado | SELECT y seguimiento autorizado | Administración verificada; no por valor enviado desde frontend |
| admin_psicologia | SELECT y seguimiento autorizado | Denegado | No puede elevarse ni administrar otras cuentas |
| admin_dentista | Denegado | SELECT y seguimiento autorizado | No puede elevarse ni administrar otras cuentas |
| Traslados, Comidas y demás roles | Denegado | Denegado | Conservar su función existente sin privilegios clínicos |
| Sin sesión o Auth anónimo | Denegado | Denegado | Sin escritura que permita crear/asignar roles |

No INSERT ni DELETE clínico desde la web. INSERT de fixtures sólo por operador autorizado y script acotado. No conceder TRUNCATE/TRIGGER/REFERENCES a usuarios web clínicos. UPDATE sólo de columnas de seguimiento; no id, paciente_id ni atendido_por. SELECT también es necesario para UPDATE; una respuesta sin filas no prueba persistencia.

## Dependencia de compatibilidad que impide aplicarlo ahora

Gestión de Usuarios usa un cliente global SUPABASE_KEY para SELECT/UPDATE/DELETE sobre perfiles, sin JWT aislado por petición. Se verificó en main y en el árbol local. Las altas Auth Admin pasan roles en user_metadata; login/register también escribe perfiles desde un cliente compartido.

No es seguro simplemente revocar escritura pública, cambiar el trigger o activar la propuesta anterior: hay que adaptar y verificar consumidores antes. Mantener una excepción de escritura pública permitiría eludir la protección. Añadir service_role al backend clínico tampoco resuelve la autorización y está descartado.

No se conocen las variables privadas efectivas de Render, y la prueba HEAD de esa ruta agotó tiempo. No se afirma haber probado una regresión de su backend ni garantizar su continuidad después del cambio. No se permite desplegar en esta fase. Por eso no se ha confirmado ningún cambio remoto ni se ha aplicado una mitad de los controles.

## Plan mínimo, previo a una nueva intervención

1. Mantener el código clínico con clave publishable y JWT ordinario verificado por petición. Corregir consumidores de perfiles para ese mismo patrón; no compartir sesiones entre usuarios.
2. Definir un rol canónico protegido. app_metadata administrado es una fuente confiable posible; nunca confiar en user_metadata. Si se usa perfil como fuente, su escritura debe quedar protegida antes de autorizar por él.
3. Resolver altas y cambios de rol de Gestión de Usuarios junto con el trigger. No migrar automáticamente los roles existentes desde metadatos editables ni modificar cuentas ajenas a los fixtures sin revisión específica. Conservar el alta legítima de administradores y evitar que un autorregistro elija admin.
4. Para perfiles: SELECT propio y los campos mínimos necesarios para administración/joins; UPDATE propio sólo de campos no sensibles al rol; administración de otras cuentas sólo con sesión y rol canónico de administrador. Evitar recursión de políticas; no añadir SECURITY DEFINER para saltarse RLS. No conceder INSERT/UPDATE/DELETE públicos sobre roles.
5. Para las clínicas: retirar las cuatro políticas públicas auditadas, revocar privilegios públicos/anon y grants innecesarios de authenticated; conservar RLS activado. SELECT y UPDATE a authenticated con predicado de sesión no anónima y rol canónico admin o responsable del área.
6. UPDATE debe repetir la autorización en USING y WITH CHECK, además del GRANT por columnas. En Psicología: tipo_atencion, motivo_consulta, diagnostico_inicial, numero_sesion, estatus_caso, fecha_sesion. En Dental: motivo_consulta, diagnostico, tratamiento_realizado, costo_recuperacion, fecha_atencion. No ampliar columnas ni derechos de identidad.
7. Confirmar dependencias de funciones, privilegios heredados, vistas y cualquier RPC antes de ejecutar: la captura actual de FK/trigger no equivale a una auditoría de todos los objetos de la base.
8. Respaldar otra vez y probar el cambio transaccional antes de COMMIT. Coordinar la versión compatible desplegada y su verificación; si no se permite actualizarla, no aplicar un corte que pueda romperla.
9. Crear siete cuentas sintéticas por Auth Admin API/panel, con correo confirmado y app_metadata de fixture/rol asignado administrativamente. No insertar directamente en auth.users.
10. Sembrar sólo mediante DATOS_PRUEBA_CLINICOS.sql en modo académico autorizado. Probar JWT reales por REST y por Flask, incluidas negativas de SELECT/UPDATE/INSERT/DELETE, cambio de identidad, autoelevación y manipulación de user_metadata. No exigir que una denegación SELECT siempre sea HTTP 403: RLS puede producir lista vacía; debe demostrar ausencia de filas ajenas.
11. Mantener CLINICAL_ENABLE_UPDATES=false hasta aprobar UPDATE real por rol; después habilitar sólo el proceso de prueba, actualizar desde UI y comprobar con una consulta nueva. Conservar default false en código/configuración ejemplo.
12. Validar login, Gestión de Usuarios, Traslados y los tres submódulos de Comidas, con cuentas/filas ficticias. No declarar regresión superada por una carga de dashboard o mocks.

## Reversión

No hay cambios remotos que revertir. En una futura transacción no confirmada, ROLLBACK es la primera defensa. Si se confirma una etapa, preparar y revisar la inversa exacta de ese delta antes de ejecutarla; no restaurar automáticamente permisos públicos inseguros ni desactivar RLS como solución. El JSON respalda definiciones, no datos ni toda la infraestructura.

## Fundamento técnico consultado

[Documentación oficial de RLS](https://supabase.com/docs/guides/database/postgres/row-level-security): grants y políticas se evalúan conjuntamente; UPDATE requiere visibilidad SELECT. La skill de Supabase también exige no usar metadatos editables para autorización y verificar con consultas reales. La preparación no demuestra que estos controles estén aplicados.
