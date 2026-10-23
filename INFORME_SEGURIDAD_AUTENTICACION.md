# FORMADIG — Seguridad y autenticación

23 de octubre de 2026. Rama `fix/autenticacion-seguridad`, creada desde el estado local cuyo HEAD era `405ea508bfd9db69b47f9813d89d1a7fe2f83316`.

**Dictamen: implementación local preparada; publicación de producción pendiente.** No se hizo push, no se modificó Render y no se ejecutaron migraciones ni escrituras Auth/perfiles en Supabase de producción. Se inspeccionaron exclusivamente metadatos mediante SELECT en SQL Editor. El SQL propuesto se probó en instancias PostgreSQL nuevas, locales y temporales con datos ficticios y funciones Auth simuladas.

## 1. Estado del login local

La configuración pública de `.env` se conserva ignorada por Git. SUPABASE_URL está definida, SUPABASE_KEY es pública y `/auth/v1/settings` respondió HTTP 200 en una comprobación de lectura. `CLINICAL_ENABLE_UPDATES=false`. Esto prueba configuración y conectividad de Auth, no un inicio de sesión real.

El flujo implementado es: validar configuración → cliente SDK independiente por solicitud → sign_in_with_password → get_user con el token recibido → consultar el perfil por el UUID verificado → exigir coincidencia exacta de app_metadata.role y perfiles.rol entre los cinco roles web permitidos → entregar sesión al frontend. `/api/auth/me` revalida identidad y rol desde el servidor. Ni user_metadata, cabeceras X-User-Role, cuerpo JSON ni localStorage conceden permisos.

Los ensayos automatizados de login usan mocks; el navegador ejecutó el formulario real y dashboard con respuestas Auth simuladas. **No se probó login real ni una cuenta personal.** Falta una cuenta de ensayo identificada y autorizada, con contraseña introducida localmente por su titular, perfil propio y rol administrado coincidente. Para la matriz completa hacen falta cinco cuentas de ensayo, una por rol, y autorización de lectura de sus propios perfiles. No se enumeraron cuentas reales ni se leyeron expedientes.

## 2. Correcciones realizadas y conservación en Git

Se mantuvieron las correcciones y pruebas de la intervención anterior, sin borrar archivos ignorados. Esta entrega se conserva mediante un commit local en `fix/autenticacion-seguridad`; su identificador se obtiene con `git log -1 --format=%H`. No se movió main ni se fusionaron de nuevo las ramas. Los informes anteriores se incluyen como antecedentes; este documento describe el estado actual.

Cambios funcionales:

- Login informa las variables faltantes sin revelar valores, rechaza claves privilegiadas y URL inapropiada, usa clientes por solicitud, verifica identidad mediante Auth y devuelve respuestas sin caché. Registro heredado que escribía roles editables permanece bloqueado.
- `clinical/security.py` centraliza los cinco roles canónicos y la comprobación identidad/perfil. Psicología, Dentista y Gestión de Usuarios reutilizan ese criterio.
- Transporte y los tres módulos de Comidas exigen Bearer verificado y el rol del área; sus clientes PostgREST llevan el JWT de la solicitud, sin sesión global compartida. Transporte deja de confiar en el rol/email enviado por cabecera.
- `formadig-core.js` consulta `/api/auth/me`, elimina sesiones rechazadas y corrige roles locales manipulados. Auth.fetch añade el token a la API del mismo origen. El nombre del perfil se escapa antes de insertarlo en el header.
- Los scripts de los módulos envían JWT también en las lecturas. No se cambió HTML/CSS ni la aplicación móvil.
- Mi Perfil usa Auth.getUser en vez de decodificar un JWT sin verificar, no imprime datos personales y exige una fila devuelta después de guardar para evitar un falso éxito ante UPDATE sin efecto.
- Gestión de Usuarios sólo permite admin canónico. Las altas preparadas asignan app_metadata.role mediante Auth Admin; ya no copian rol en user_metadata. No hubo altas reales. Los cambios de rol por PATCH siguen bloqueados; tampoco se reenvía rol en una edición ordinaria de perfil. La baja de perfiles queda bloqueada con 409 hasta coordinar Auth, sesiones y dependencias, evitando cascadas clínicas e identidades incompletas.
- Se cerró el acceso alternativo de soporte: Chatbot exige sesión, tiene una lista cerrada de tablas por área y rechaza exportaciones de clínicas/perfiles. Su contexto toma rol/email de la identidad verificada, no del JSON. Las descargas web usan JWT en cabecera, nunca en URL.
- SMS deja de preferir service_role para saltarse RLS. Usa cliente público con JWT, identifica al remitente desde la sesión y aplica la restricción de roles existente en el menú. El webhook queda bloqueado con 503: necesita validación de firma y un flujo de servicio acotado antes de volver a operar. No se enviaron SMS ni consultas Gemini durante las pruebas.

El backend `modulos/perfil/logica/perfil_backend.py` no está entre los 11 blueprints de run.py; la pantalla activa usa perfil.js directamente. Las copias históricas y servidores independientes no quedan certificados por estos cambios. No se publicó ninguna de ellas.

Las capturas de `output/playwright` se preservan localmente sin incorporarlas al commit, para evitar mezclar binarios regenerados con la corrección. `.env`, evidencias privadas previas, entornos, cachés y directorios temporales quedan excluidos.

## 3. Compatibilidad con usuarios existentes

El código histórico y el trigger confirmado explican la incompatibilidad: el alta administrativa enviaba rol por user_metadata.rol; handle_new_user lo copiaba a perfiles.rol. El login heredado también aceptaba user_metadata.role como respaldo. Eso no acredita que un rol histórico haya sido otorgado por una persona autorizada. No se inspeccionaron filas de cuentas para atribuir su origen individual.

| Rol canónico | Operación web protegida |
|---|---|
| admin | Gestión de Usuarios, Transporte, Comidas y consulta de ambas áreas clínicas |
| admin_traslados | Transporte; sin administración de cuentas ni clínica |
| admin_desayunos | Tres módulos de Comidas; sin SMS, administración de cuentas ni clínica |
| psicologo | Consulta de Psicología; sin Dental ni administración de cuentas |
| dentista | Consulta de Dental; sin Psicología ni administración de cuentas |

Chatbot mantiene acceso de soporte para los cinco roles, con tablas de datos limitadas a su área. Las autorizaciones del backend y de RLS deben coincidir; que una página estática o enlace sea visible no permite leer datos de la API.

Cuentas sin app_metadata.role confiable, con perfil faltante, UUID distinto o rol discrepante se rechazan. **No se convierten automáticamente los roles anteriores.** Antes del corte, un responsable debe aprobar cada UUID/rol y autorizar su aprovisionamiento mediante Auth Admin, conservando los demás metadatos y sin deducir privilegios de user_metadata. Roles distintos de los cinco, incluidos los alias históricos directora/desarrollador, requieren revisión explícita; no se traducen automáticamente a admin.

La propuesta conserva SELECT del perfil propio para login, Mi Perfil y la subconsulta RLS de Transporte. Conserva edición propia de campos no sensibles para cuentas registradas no anónimas, incluidas cuentas no web; no concede edición de rol/id. Administración verificada puede editar esos mismos campos en otros perfiles. El borrado y los cambios de rol son operaciones separadas.

Los joins clínicos a otros perfiles pueden devolver nombre nulo bajo la política mínima propia/admin: clinical-ui ya muestra paciente_id como respaldo. Si se requieren nombres de pacientes para profesionales, falta aprobar una proyección mínima específica; no se abre todo perfiles para resolverlo. La compatibilidad móvil sobre estas tablas compartidas necesita validación antes del corte, aunque no se modificó su código.

## 4. Riesgos RLS confirmados

MCP volvió a responder sin autorización. Se utilizó la sesión autenticada de SQL Editor únicamente para SELECT de pg_catalog/pg_policies. El autoguardado no se usó para publicar consultas; quedaron borradores sin guardar. Hubo errores sintácticos al editar/reintentar una consulta; no causaron cambios de esquema o datos.

La evidencia actual y las consultas reproducibles están en `docs/security/METADATOS_CONFIRMADOS_20261023.md` y `METADATOS_SOLO_LECTURA.sql`:

- perfiles tiene RLS desactivado, tres políticas públicas sin restricción y privilegios amplios para anon/authenticated.
- Psicología y Dental tienen RLS activo pero SELECT e INSERT públicos permisivos con condiciones true. No hay UPDATE/DELETE clínicos permitidos por políticas, pero los grants siguen siendo excesivos; TRUNCATE no queda protegido por RLS.
- El trigger Auth sigue copiando rol desde raw_user_meta_data. Es SECURITY DEFINER, sin search_path fijado y con ACL EXECUTE amplia.
- anon/authenticated no tienen BYPASSRLS ni membresías adicionales observadas. Las ACL de columnas son NULL.
- Perfiles enlaza con Auth, clínicas, Transporte y chatbot_historial. Existen cascadas al eliminar pacientes/perfiles. La política RLS Traslados consulta perfiles.rol; se comprobó su condición exacta y se reprodujo en laboratorio.

Son hallazgos actuales de metadatos, no sólo del informe anterior. No se intentó explotar acceso por REST ni consultar información clínica. La exposición efectiva de Data API, permisos de esquema y todas las dependencias dinámicas no están certificadas. El éxito del laboratorio no significa que producción esté corregida.

## 5. Propuesta SQL revisada

Archivos generados con Supabase CLI, **sin aplicar en producción**:

1. `supabase/migrations/20261023202836_formadig_roles_protegidos.sql`: fase A. Crea un registro de roles en esquema privado, con RLS de lectura propia y sin escrituras para clientes web. Una función SECURITY INVOKER compara el registro con el claim firmado, evitando recursión en perfiles y negando tokens con rol antiguo. Sustituye el trigger heredado por uno privado de aprovisionamiento, que toma el rol exclusivamente de raw_app_meta_data. No recorre ni transforma cuentas existentes.
2. `supabase/migrations/20261023202914_formadig_rls_corte_coordinado.sql`: fase B. Exige aprobación explícita por conexión, al menos un admin aprovisionado, concordancia de todas las cuentas con rol web conocido y un inventario de políticas sin cambios. Revoca permisos amplios, activa RLS en perfiles y sustituye las políticas públicas auditadas por propias/admin en perfiles y por área en clínicas. Sólo concede consulta clínica; no INSERT, UPDATE, DELETE ni TRUNCATE clínicos.

El trigger privado es SECURITY DEFINER exclusivamente para sincronizar Auth con el registro protegido y perfiles, sin SQL dinámico, con search_path vacío y ejecución retirada a clientes. No es una función genérica para eludir RLS de consultas. No se utiliza service_role para datos clínicos; la clave administrativa del backend sólo queda para altas Auth legítimas tras comprobar admin.

Los archivos usan transacciones, nombres exactos y DROP sin CASCADE: un cambio de dependencias provoca error y exige revisión. No modificar ni ejecutar borradores anteriores sobre la base compartida. Falta revisarlos nuevamente contra el esquema real al autorizar la intervención y verificar configuración Data API del esquema privado. No se preparó una restauración automática que reponga permisos públicos inseguros.

## 6. Resultados de pruebas

| Prueba | Resultado | Alcance |
|---|---|---|
| Python unittest tests_clinical | 34/34 | Identidad, roles, API, denegaciones, clientes por solicitud y soporte con mocks |
| Node frontend + auth | 12/12 | Contratos, menús, sesión, 401/403, rol manipulado, escape de nombre y envío de JWT |
| Playwright visual_flow | 29/29 en proceso nuevo | Clínica sintética en memoria, incluido logout con redirección y API 401 |
| Playwright visual_fields | 7/7 | Validaciones de campos sintéticas |
| Playwright visual_auth | 7/7 | Formulario y dashboard reales, respuestas Auth simuladas |
| PostgreSQL 16.15 aislado | 89/89 | Ejecución real del SQL propuesto sobre fixtures y funciones Auth/JWT simuladas |
| Sintaxis JS modificados / git diff --check | Correctos | Verificación local |
| Auth settings público | HTTP 200 | Configuración/conectividad, no credenciales de usuario |
| Login, persistencia y regresión real | Pendientes | Sin cuenta de ensayo ni escrituras remotas autorizadas |

El laboratorio crea un clúster nuevo en TEMP, ligado a 127.0.0.1 y a un puerto temporal, sin usar variables PG ni URLs Supabase del entorno. Lo detiene al finalizar y conserva sus archivos ficticios para inspección. Verifica SELECT directo por rol, denegación de INSERT/UPDATE/DELETE/TRUNCATE clínicos, imposibilidad de cambiar rol por REST/SQL, edición administrativa y propia no sensible, rechazo de tokens con rol anterior, no promoción de user_metadata, preservación de cuentas históricas y aborto del corte sin aprobación o sin aprovisionamiento. No usa ni acredita JWT firmados reales, PostgREST real ni el motor Auth real.

Se conservan los resultados en `output/rls-lab-result.json` y `output/auth-security-validation.json`. Los ensayos iniciales detectaron un residuo de logging en Transporte y un problema de configuración del entorno de mocks; se corrigieron y las suites completas aprobaron. El primer arranque del laboratorio dejó abierto un pipe de pg_ctl en Windows; se detuvo exclusivamente ese clúster temporal y se corrigió el manejo de logs/subprocesos.

También se registra el fallo visual previo: un caso esperaba quedarse en la página clínica después del logout; ahora exige redirección al login y API 401. Otra repetición reutilizó registros de memoria y falló cuatro casos de búsqueda/selección: se comprobaron dos coincidencias por marcador, se arrancó una demo nueva según el procedimiento y se repitieron las mismas aserciones. No se aumentaron timeouts ni se debilitaron las comprobaciones para obtener aprobación.

Comandos de repetición:

```powershell
& ./.venv-local/Scripts/python.exe -B -m unittest discover -s tests_clinical -p 'test_*.py'
node --test tests_clinical/test_frontend.cjs tests_clinical/test_auth.cjs
& ./.venv-local/Scripts/python.exe -B scripts/verify_rls_isolated.py --pg-bin 'C:\Program Files\PostgreSQL\16\bin'
```

Para navegador, usar una demo nueva de `tests_clinical.serve_synthetic --enable-creation --enable-updates`; ejecutar visual_flow.js una sola vez por proceso, después visual_fields.js. visual_auth.js intercepta Auth en localhost y es explícitamente sintético. Ninguna bandera sintética se habilitó en run.py ni en producción.

## 7. Secuencia segura para actualizar Supabase y backend

Esta secuencia es una propuesta: no autoriza ni ejecuta pasos remotos.

1. Revisar el commit local, los cambios de comportamiento restringidos y las dos migraciones. Probar en un entorno de ensayo separado con Supabase Auth/PostgREST reales y datos ficticios.
2. Inventariar consumidores web/móvil, dependencias y callbacks. Obtener autorización de lectura de cuentas de ensayo y un manifiesto aprobado de UUID/rol. No exportar datos personales al repositorio.
3. Preparar respaldo y reversión exacta del delta autorizado; establecer una ventana coordinada para altas/cambios de roles. No prometer un corte sin interrupciones antes de ensayarlo.
4. Bajo autorización específica, aplicar fase A y verificar el trigger con cuentas ficticias. No habilitar todavía lectura/escritura clínica real. Fase A por sí sola no corrige las políticas públicas.
5. Aprovisionar explícitamente todas las cuentas web aprobadas mediante Auth Admin, sin copiar roles de metadatos editables. Confirmar perfil, registro protegido y app_metadata; conservar metadatos ajenos al rol. Revisar también cuentas antiguas cuyos perfiles estén ausentes. Refrescar sesiones autorizadas; probar los cinco roles y conservar acceso administrativo antes de continuar.
6. Validar en ensayo la nueva versión completa, incluidos Mi Perfil, Gestión de Usuarios, Transporte, Comidas, descargas de Chatbot y SMS. El webhook y las bajas continúan bloqueados hasta tener sus procedimientos seguros. Comprobar consumidores móviles sin cambiar su código de forma implícita.
7. Con autorización de despliegue y ventana acordada, coordinar fase B y backend compatible. La versión anterior usa accesos sin JWT y no puede darse por compatible con los nuevos grants. No aplicar B mientras dependa de esos accesos ni dejar la transición parcialmente abierta como solución definitiva. Si falta una condición, no empezar el corte.
8. Verificar con cuentas ficticias los accesos positivos/negativos tanto por Flask como directamente por REST, roles desactualizados y autoelevación. Una lista vacía puede ser la denegación SELECT correcta; una respuesta HTTP 200 sin filas no prueba persistencia.
9. Mantener CLINICAL_ENABLE_UPDATES=false y sin creación clínica. Revisar SHA desplegado, errores de arranque y regresión funcional antes de aprobar publicación. Ante error, abortar transacciones no confirmadas o mantener la aplicación restringida y corregir el delta; no volver a conceder acceso público ni desactivar RLS automáticamente.

## 8. Dependencias pendientes de autorización

- Aplicar o modificar esquema, trigger, políticas y privilegios de producción.
- Leer perfiles/cuentas de prueba y asignar app_metadata a UUID aprobados; crear fixtures reales si se autoriza.
- Probar Auth/PostgREST reales y regresión funcional con datos ficticios controlados.
- Aprobar el alcance de lectura de pacientes por profesionales y la proyección mínima de nombres.
- Resolver firma y permisos del webhook SMS, ciclo de baja Auth/perfil/sesiones y eventuales cambios de rol coordinados.
- Verificar permisos de tablas de Transporte, Comidas, sms_logs y contexto Chatbot fuera de las tres tablas auditadas. Los guards locales no sustituyen sus políticas directas.
- Validar consumidores móviles, servidores independientes y vistas/RPC/SQL dinámico no cubiertos. No se modificaron ni se certifican.
- Autorizar publicación de la rama/PR y posteriormente main/Render. No existe autorización de push en esta fase.

## 9. Recomendación final

Listo para revisión: código local de autenticación/autorización, pruebas sintéticas, laboratorio PostgreSQL reproducible, evidencia de metadatos actuales y propuesta SQL en dos fases.

**Todavía no es seguro publicar esta corrección en producción.** Primero deben aprobarse y ensayarse el aprovisionamiento de cuentas y el corte coordinado con permisos reales. Los riesgos RLS remotos están confirmados y permanecen sin modificar. No se declara resuelta la seguridad de Supabase, probado el login real ni certificadas operaciones clínicas.

Referencias técnicas consultadas: [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [gestión de datos de usuarios](https://supabase.com/docs/guides/auth/managing-user-data). El changelog de Supabase también se revisó; no se actualizaron versiones ni extensiones del servidor.
