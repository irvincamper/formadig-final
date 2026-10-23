# FORMADIG — Activación Supabase real

## Estado vigente tras integración por CLI (23 de octubre de 2026)

Esta sección sustituye las conclusiones de estado anteriores, que se conservan abajo como antecedente de la contención. **Fase A aplicada y verificada; contención conciliada con el historial; Fase B, cuentas y publicación pendientes.**

### Operaciones reales y secuencia

1. Se comprobó que el vínculo CLI apunta exclusivamente a DIF `ctiqbycbkcftwuqgzxjb`. `db query --linked` funciona; no se volvió a depender del MCP.
2. Se leyeron completas las tres migraciones y se contrastaron políticas, columnas, restricciones, ACL, dependencias y trigger remotos. Antes del alta seguían nueve políticas: tres de perfiles, cuatro clínicas heredadas y dos restrictivas de contención. El historial oficial y el esquema privado todavía no existían.
3. Se conservaron definiciones del trigger/función/ACL/restricciones y metadatos en `output/cli-schema-backup-before-a.json` y `output/cli-phase-a-preflight.json`. Son evidencia y respaldo de las definiciones afectadas, **no un respaldo íntegro de datos ni una restauración probada**. No se exportaron expedientes.
4. Para aislar la fase se creó una carpeta temporal con el vínculo del proyecto y **únicamente** `20261023202836_formadig_roles_protegidos.sql`. El dry-run enumeró sólo ese archivo. `supabase migration up --linked --workdir ...` aplicó la Fase A mediante el mecanismo oficial; no se ejecutó un push del conjunto completo.
5. Se verificaron el trigger privado `sync_auth_web_role()`, el registro vacío, la ausencia de EXECUTE para clientes sobre el trigger privilegiado y la entrada oficial `20261023202836`. Ninguna cuenta histórica se convirtió automáticamente.
6. Se comparó la contención efectivamente instalada: seis políticas clínicas totales, dos denegaciones restrictivas, ambas tablas con RLS y sin privilegios SELECT/INSERT/UPDATE/DELETE/TRUNCATE para anon/authenticated. Después se ejecutó `migration repair 20261023214516 --status applied --linked`, **sólo para registrar el delta ya ejecutado anteriormente por SQL Editor**. No se ejecutó de nuevo su CREATE POLICY ni se alteró su protección.
7. El listado oficial final muestra A y contención aplicadas; `20261023202914` sigue pendiente. La tercera migración es una medida de cierre preventivo: el estado real fue contención primero, Fase A después y Fase B todavía no. Su registro no abre acceso ni concede roles.

### Bloqueos confirmados para B y backend

Hay **ocho cuentas web históricas sin rol administrado en Auth**: dos perfiles admin, cuatro admin_traslados y dos admin_desayunos. Todas carecen de `raw_app_meta_data.role`. No se copió `perfiles.rol` al registro: el origen histórico no es confiable. La Fase B mantiene su preflight para detener el corte ante esta situación. El backend nuevo exige Auth administrado + perfil coincidente; publicarlo ahora bloquearía esas cuentas.

El inventario con UUID, rol histórico y rol administrado se guardó exclusivamente en `%LOCALAPPDATA%/FORMADIG/security-activation/REVISION_ROLES_EXISTENTES.json`, con ACL restringida al usuario de Windows, fuera de Git. Se solicitó revisión individual del titular para definir el aprovisionamiento permitido; no se modificaron esas ocho cuentas. No contiene contraseñas.

La revisión de dependencias también confirmó RLS deshabilitado en Traslados, los tres módulos alimentarios y sms_logs. La Fase B propuesta sólo cubre perfiles y las dos tablas clínicas; por sí sola **no certifica autorización directa de toda la aplicación**. Su diseño y la regresión web por rol siguen pendientes. No se modificaron esas tablas para ocultar esta incompatibilidad ni se afirma compatibilidad móvil.

### Tres cuentas y credenciales

La clave de Auth Admin está presente en `.env`, pero la solicitud al endpoint administrativo respondió **HTTP 401**. La comprobación local sin mostrar su contenido indicó que no tiene formato JWT service_role ni sb_secret_. Presencia en el archivo no significa credencial válida. Se solicitó sustituirla por la clave administrativa de DIF únicamente en el archivo local ignorado; no se intentó crear cuentas por SQL ni usarla contra tablas para saltar RLS.

**Cuentas reales creadas en esta intervención: cero. Login real de las tres cuentas: pendiente.** Los tres correos autorizados siguen siendo los de la conversación del titular; antes de un alta se repetirá la búsqueda exacta de esas identidades para evitar duplicados. No se generaron ni entregaron contraseñas reales. Las credenciales demo existentes siguen siendo exclusivamente locales.

### Validación, Git y publicación

La Fase A conserva el SQL previamente validado en el laboratorio: 47 pruebas Python, 12 Node y 96 controles PostgreSQL aislados aprobados en la fase anterior. No son pruebas de login Supabase. La verificación de aplicación A y de contención sí se hizo sobre DIF real mediante consultas de metadatos y agregado de roles, sin expedientes. Advisors de seguridad antes/después y el historial se conservaron en `output/cli-advisors-*.json` y `output/cli-migration-history-after-a.json`; no se declara que toda la base esté libre de riesgos.

Los cambios siguen en `fix/autenticacion-seguridad`. Se conservaron capturas, .env, archivos ignorados y trabajo frontend; no se modificó HTML/CSS ni la aplicación móvil. **No hubo push, merge a main ni despliegue Render.** El alcance autorizado permite prepararlos, pero faltan la conciliación de usuarios, los permisos de módulos existentes y las pruebas Auth/PostgREST reales. Las escrituras clínicas permanecen cerradas.

Para continuar: corregir la credencial administrativa; revisar explícitamente las ocho identidades históricas; preparar el cierre de los permisos directos aún abiertos en módulos web; provisionar las cuentas por Auth Admin con acceso operativo retenido hasta la validación; conciliar los roles aprobados; ensayar el corte de perfiles/RLS/backend; aplicar B de forma aislada sólo cuando sus preflights y la compatibilidad pasen; validar positivos y negativos con JWT reales y datos ficticios autorizados; entonces integrar backend en GitHub/Render y entregar las contraseñas por archivo privado local. No reabrir políticas públicas para solucionar fallos.

---

## Antecedente: primera contención (estado anterior, no vigente para Fase A/CLI)

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
