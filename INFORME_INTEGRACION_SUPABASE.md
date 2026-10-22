# FORMADIG — integración académica con Supabase

Nota de fase posterior: la adaptación local solicitada después se documenta en INFORME_ADAPTACION_MODULOS.md. Los roles vigentes son psicologo/dentista, sin migración remota. En esa fase el MCP supabase_formadig_readonly ya respondió correctamente a search_docs y a una consulta de columnas (17 columnas clínicas); no se habilitaron escrituras. El estado de acceso y los nombres de rol narrados debajo corresponden a la captura anterior, no al contrato local nuevo.

Actualizado: 21 de octubre de 2026 (las capturas posteriores a las 18:00 de México tienen fecha UTC 22). Rama: `feat/psicologia-dentista`, base `c74e6f7`. Cambios previos conservados.

**Estado: inspección real y respaldo completados; escrituras detenidas por incompatibilidad de seguridad con la administración de usuarios existente. No se declara una integración funcional validada.**

## Autorización y alcance vigentes

El titular autorizó expresamente el proyecto académico **DIF**, `ctiqbycbkcftwuqgzxjb`, incluyendo fixtures, cuentas sintéticas y controles RLS. Ya NO se exige otro proyecto ni otra rama Supabase. La etiqueta técnica main PRODUCTION del panel no convierte el proyecto académico en una institución real.

La confirmación posterior autoriza aplicar controles desde el navegador, pero exige detenerlos si no se puede garantizar compatibilidad segura con login, Gestión de Usuarios, Traslados y Comidas, sin modificar/desplegar Render. Esa condición determina la pausa actual; no falta una nueva autorización para utilizar DIF.

No se trabajó sobre la aplicación móvil. No se modificó Render ni se hicieron commits, push o merge.

## Acceso comprobado

- MCP oficial, get_project de la referencia exacta: `MCP error -32600: You do not have permission to perform this action`. Falta acceso efectivo del conector a ese proyecto; no se ha demostrado si la causa es su vinculación de cuenta/organización o permisos del token. OAuth previo no demuestra que este conector tenga ese acceso.
- El servidor Codex `supabase_formadig_readonly` configurado anteriormente conserva alcance de sólo lectura. Sus herramientas no están expuestas en este turno; no se amplió su alcance ni se almacenaron credenciales.
- Navegador autenticado: título DIF y URL exacta del SQL Editor para `ctiqbycbkcftwuqgzxjb`. Se ejecutaron nuevas consultas de catálogos y agregados. El navegador sí permitió inspeccionar; el bloqueo MCP no se presenta como imposibilidad total de acceso.
- API REST real, con clave publishable y SIN JWT: GET select=id&limit=1 de ambas tablas → HTTP 200, lista vacía. Prueba de conectividad/estado público actual, NO prueba de aislamiento RLS satisfactorio.

## Resultados reales, antes de cualquier escritura

| Comprobación | Resultado |
|---|---|
| public.modulo_psicologia | 0 registros |
| public.modulo_dental | 0 registros |
| public.perfiles | 23 registros existentes; ninguno con el prefijo de fixtures |
| Siete correos Auth reservados | 0 cuentas encontradas |
| RLS clínicas | Activado, force=false |
| RLS perfiles | Desactivado |
| Políticas clínicas | Dos por tabla: SELECT público USING true e INSERT público WITH CHECK true |
| Políticas perfiles | Lectura pública y dos de inserción pública; inefectivas como protección al estar RLS desactivado |
| ACL de las tres tablas | anon/authenticated/service_role con privilegios amplios, incluidos modificación, TRUNCATE y TRIGGER |
| ACL explícitos de columnas | 27 columnas, todos null |
| Trigger Auth | on_auth_user_created → public.handle_new_user(), SECURITY DEFINER, propietario postgres |
| Rol del perfil al registrarse | El trigger copia raw_user_meta_data->>'rol': fuente editable por el usuario |
| Seguimiento local | CLINICAL_ENABLE_UPDATES=false; no habilitado |

Las tablas clínicas vacías permiten confirmar ausencia de información clínica preexistente en ellas en ese instante. En perfiles sólo se consultaron agregados: cinco CURP y seis teléfonos no vacíos; no se leyeron ni copiaron sus valores. No es posible distinguir automáticamente si un identificador es real por su mera existencia. Se conserva la declaración académica del titular y se excluyen esos 23 perfiles de las pruebas: sólo se usarían cuentas nuevas marcadas, sin reutilizar pacientes existentes.

## Esquema confirmado en vivo

Psicología: id uuid PK default gen_random_uuid(); paciente_id uuid NOT NULL; atendido_por uuid nullable; tipo_atencion y motivo_consulta text NOT NULL; diagnostico_inicial text nullable; numero_sesion int4 default 1; estatus_caso text default 'En proceso'; fecha_sesion timestamptz default now(). Últimas cuatro columnas permiten null.

Dental: id uuid PK default gen_random_uuid(); paciente_id uuid NOT NULL; atendido_por uuid nullable; motivo_consulta text NOT NULL; diagnostico y tratamiento_realizado text nullable; costo_recuperacion numeric(10,2) nullable default 0.00; fecha_atencion timestamptz nullable default now().

En ambas tablas, paciente_id → perfiles.id ON DELETE CASCADE; atendido_por → perfiles.id ON DELETE SET NULL. perfiles.id → auth.users.id ON DELETE CASCADE; nombre_usuario tiene UNIQUE. No se introdujeron columnas.

Dependencias compartidas verificadas: traslados.registrado_por y chatbot_historial.usuario_id también referencian perfiles.id. No hay FK entrantes a las tablas clínicas en la captura. El trigger Auth afecta al alta general de usuarios.

## Respaldo verificado antes de modificar permisos

Archivo: `evidencias_supabase/20261021_seguridad_previa.json`.

Captura principal: 2026-10-22T00:00:09.986087+00:00. Contiene flags RLS y ACL de tres tablas, 27 ACL de columnas, siete políticas completas, once restricciones y trigger/función Auth. Se añadió la consulta complementaria de propietario, EXECUTE ACL y configuración de función. Sin expedientes ni secretos.

SHA-256 del archivo final:
`1EE5B7337B827BEE43AF5E7CF855BB7626F4A33614A6BB04AA3103F5585C1E6A`.

Se verificó parseo JSON, referencia y conteos contra la exportación observada. No se considera un backup integral de la base. La descarga CSV del navegador se inició, pero no se afirma que exista en Downloads: el respaldo entregado es el JSON local verificado.

Procedimiento de reversión: `evidencias_supabase/PROCEDIMIENTO_REVERSION.md`. Antes de COMMIT, ROLLBACK transaccional; después de COMMIT, reversión revisada del delta y comprobación de concurrencia, nunca desactivar RLS o reabrir permisos como solución. **No hay cambios remotos que revertir en esta fase.**

Captura visual final: `evidencias_supabase/20261021_conteos_clinicos.png`. Una consulta nueva confirmó nuevamente 0 filas por tabla; muestra el proyecto y los resultados, sin expedientes ni credenciales.

## Incompatibilidad que impide aplicar controles con seguridad ahora

Confirmado tanto en el árbol de trabajo como en el archivo de main:

- Gestión de Usuarios crea un cliente global con SUPABASE_KEY (clave pública por defecto).
- Sus lecturas y escrituras en perfiles usan ese cliente, no un cliente aislado por petición con el JWT del administrador verificado.
- Las altas por Auth Admin envían el rol en user_metadata; el trigger lo copia al perfil.
- El login/register contiene además un upsert de perfiles con un cliente compartido. El código clínico nuevo sí usa JWT por petición y rechaza claves service_role.

Proteger perfiles contra autoelevación exige cerrar la escritura pública y dejar de confiar en user_metadata. Si se retiran esos permisos sin actualizar las rutas consumidoras, sus operaciones públicas dejan de estar permitidas; mantenerlas abiertas para conservarlas incumpliría el control solicitado. El borrador RLS de desarrollo aislado, que revoca todos los accesos y reduce columnas de perfiles, tampoco es compatible directamente con esta base compartida.

No se ha inspeccionado la configuración privada efectiva de Render ni se afirma conocer qué valor tiene allí SUPABASE_KEY. HEAD sin sesión a /api/admin_usuarios/ agotó 30 segundos: no aportó evidencia de compatibilidad ni un resultado funcional. La presencia del dashboard ya abierto no prueba los flujos de escritura/login.

Sin actualizar y verificar la versión desplegada no puedo garantizar simultáneamente el endurecimiento completo y la continuidad exigida. No está autorizado desplegar. Por instrucción del titular, se detuvieron cambios remotos antes de aplicar una seguridad parcial o debilitarla. **No se intenta resolver esto añadiendo service_role al backend clínico.**

## Cambios locales de esta fase

- DATOS_PRUEBA_CLINICOS.sql acepta exclusivamente DIF mediante environment=academic-authorized, project_ref exacta y academic_approved=FORMADIG_CLINICAL_INTEGRATION_V1. Conserva el camino de desarrollo aislado.
- Conserva inspect por defecto, comprobaciones de columnas/tipos/PK/FK/nullabilidad, cuentas Auth marcadas administrativamente, propiedad de UUID, colisiones, transacciones, repetibilidad y limpieza acotada.
- El guard académico no fabrica cuentas ni habilita RLS ni seguimiento. El script completo NO se ejecutó; sí se ejecutaron consultas independientes de metadatos/conteos.
- Parser pglast: 12 sentencias SQL y un bloque PL/pgSQL, sin error sintáctico. Es validación sintáctica local, no evidencia de ejecución SQL.
- Respaldo y procedimiento de reversión; informe, matriz y propuesta actualizados.
- No se modificó código funcional en esta fase y se conservaron todos los cambios anteriores.

## Pendiente, sin declarar resultados no ejecutados

No se crearon cuentas Auth, perfiles ni atenciones sintéticas. No se ejecutó seed/clean, DDL, GRANT/REVOKE, cambios de trigger ni políticas. No se obtuvieron sesiones de prueba reales. Búsqueda, selección, historial, paginación, UPDATE, persistencia y negativas por rol siguen pendientes. Los mocks anteriores no sustituyen ninguna de esas pruebas.

Para continuar: acordar una ventana que permita coordinar el backend compatible y el endurecimiento de perfiles, o una alternativa que demuestre que los consumidores desplegados no dependen de permisos públicos. Preparar y verificar primero rutas por sesión, fuente confiable de roles y compatibilidad de altas; después aplicar controles por etapas, crear las siete cuentas sintéticas por Auth Admin/panel y ejecutar el fixture con 26 filas por área para paginación. Mantener seguimiento desactivado hasta superar UPDATE real con JWT ordinarios y negativas directas.

No es requisito crear otro proyecto Supabase ni ampliar el alcance a sistemas ajenos.
