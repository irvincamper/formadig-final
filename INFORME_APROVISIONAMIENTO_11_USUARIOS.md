# FORMADIG — Aprovisionamiento real de 11 usuarios

23 de octubre de 2026. Proyecto DIF `ctiqbycbkcftwuqgzxjb`. Rama `fix/autenticacion-seguridad`.

**Resultado: ocho identidades históricas conservadas y tres nuevas creadas en Supabase Auth; las once tienen UUID/perfil/rol administrado/registro protegido concordantes. El login real de las tres nuevas pasó. La activación clínica, el corte B y la publicación siguen bloqueados por permisos directos de base de datos todavía abiertos.**

## 1. Migraciones realmente aplicadas

| Migración | Estado real |
|---|---|
| `20261023202836_formadig_roles_protegidos.sql` | Aplicada anteriormente por CLI y verificada nuevamente. |
| `20261023214516_formadig_clinical_containment.sql` | Contención aplicada anteriormente por SQL Editor y conciliada con el historial oficial mediante repair; permanece activa. No se volvió a ejecutar. |
| `20261023202914_formadig_rls_corte_coordinado.sql` | **No aplicada**. Sus preflights de cuentas/políticas pasaron en `BEGIN READ ONLY` con `ROLLBACK`; no se ejecutaron sus ALTER/DROP/GRANT. |

No se hizo db push indiscriminado. El historial final contiene A y contención. Las escrituras clínicas siguen denegadas y tampoco se concedió lectura de expedientes durante este trabajo.

## 2. Ocho identidades históricas

Se cotejaron individualmente los ocho UUID, correos y perfiles con el inventario privado y con la tabla de autorización del titular. Dos conservaron admin, dos admin_desayunos y cuatro admin_traslados. Se modificó únicamente `app_metadata.role` por Auth Admin, fusionándolo con los metadatos administrativos existentes. No se copiaron roles de user_metadata.

Después de cada actualización se leyó de nuevo la misma identidad por UUID y se comprobó la conservación de correo y metadatos ajenos al rol. Se conservó una copia privada anterior de app_metadata. El trigger A actualizó perfil/registro sin recrear identidades. No se enviaron campos de contraseña ni se cambiaron las contraseñas históricas. Ninguna otra cuenta recibió roles.

La relación individual con UUID/correo/los tres roles está en el archivo privado `INVENTARIO_11_USUARIOS_VERIFICADOS.md`, fuera de Git. El informe versionado conserva únicamente resultados agregados.

## 3. Tres identidades nuevas

| Identificador de prueba solicitado | Rol | Resultado |
|---|---|---|
| `[identificador privado omitido]` | admin | Creada, confirmada y login real aprobado. |
| `[identificador privado omitido]` | psicologo | Creada, confirmada y login real aprobado. |
| `[identificador privado omitido]` | dentista | Creada, confirmada y login real aprobado. |

Se verificó primero que no existían para evitar duplicados. Se utilizó Auth Admin create_user con `email_confirm=True`, sin invitaciones, generate_link, mensajes ni cambios globales de verificación. Supabase aceptó los tres identificadores; no se sustituyeron por direcciones reservadas. No se afirma titularidad de los buzones. Los nombres de perfil son explícitamente de prueba.

Las contraseñas son aleatorias, diferentes y de 40 caracteres; se generaron fuera del código y se guardaron antes del alta para no perderlas ante una respuesta incompleta. No se imprimieron ni se incluyeron en informes, capturas, trazas o Git.

## 4. Correspondencia de las once cuentas

Consulta final real: 11 registros protegidos, 11 coincidencias Auth/perfil/registro. Totales: admin 3, admin_traslados 4, admin_desayunos 2, psicologo 1 y dentista 1. El trigger privilegiado no es ejecutable por clientes web. Evidencias sin secretos: `output/eleven-provisioning-result.json` y `output/eleven-final-registry.json`.

La clave administrativa se leyó exclusivamente de .env para operaciones Auth Admin. Las consultas PostgreSQL se hicieron por CLI autorizado. Los ensayos ordinarios utilizaron clave pública y JWT del propio usuario, nunca service_role para tablas.

## 5. Autenticación real y navegador

Las tres nuevas pasaron login por correo/contraseña contra Supabase, GetUser para validar identidad, lectura de su perfil y `/api/auth/me` en el backend Flask local real. Playwright/Chrome ejecutó el formulario web, dashboard, menú por rol, manipulación de LocalStorage, logout y redirección con token inválido. No hubo respuestas Auth simuladas en esos recorridos ni se leyeron expedientes.

El primer ensayo de navegador falló en dos comprobaciones al leer el menú durante la recarga de revalidación. Se conservó `output/eleven-real-browser-initial.json`. El ensayo final espera el rol y menú finales, manteniendo todas las aserciones; las tres cuentas aprobaron. No se alteró HTML/CSS para conseguirlo.

Los ocho históricos se verificaron individualmente mediante Auth Admin y PostgreSQL. **No se ensayaron sus contraseñas**: no se disponía de ellas y no se solicitaron ni restablecieron. La prueba de contraseña real corresponde a las tres cuentas nuevas.

## 6. Matriz de permisos web

| Rol | Dashboard | Usuarios | Traslados | Tres áreas alimentarias | Psicología | Dentista |
|---|---|---|---|---|---|---|
| admin | Sí | Sí | Sí | Sí | Capacidad autorizada | Capacidad autorizada |
| admin_traslados | Sí | No | Sí | No | No | No |
| admin_desayunos | Sí | No | No | Sí | No | No |
| psicologo | Sí | No | No | No | Capacidad autorizada | No |
| dentista | Sí | No | No | No | No | Capacidad autorizada |

Es la matriz del backend: roles de áreas históricas ensayados con mocks y verificados en Auth/registro; tres roles nuevos con JWT reales. Las capacidades clínicas autorizadas devolvieron 200; las áreas prohibidas devolvieron 403. Para los profesionales, Usuarios/Traslados/Comidas rechazaron incluso X-User-Role y parámetros role=admin. No se descargaron listados de beneficiarios para demostrar un permiso.

**Capacidad autorizada no significa acceso clínico activado:** la contención aún hace que ambas tablas clínicas devuelvan 403 incluso al personal. Sus pantallas de datos no se consideran funcionales hasta el corte seguro. Las funciones CRUD no clínicas tampoco se certifican con datos reales en este ensayo.

## 7. Seguridad y fallos confirmados

- Cambiar user_metadata de las dos cuentas profesionales nuevas a rol admin no cambió su autorización: `/me` conservó el rol aprobado y Usuarios siguió denegado. Se restauró exactamente su metadata original al terminar.
- LocalStorage y encabezados inventados no concedieron permisos en Flask. El navegador repuso el rol verificado. Token inválido rechazado.
- Se implementó `/api/auth/logout` con JWT ordinario y scope local; el frontend solicita revocación remota y limpia su almacenamiento. Refresh tokens rechazados tras logout. Los JWT usados en estos ensayos también fueron rechazados inmediatamente por GetUser; esto no se generaliza como garantía sobre cualquier JWT hasta su expiración.
- Creación clínica devolvió 405; flags de creación/actualización falsos. No se ejecutaron escrituras ni consultas de expedientes clínicos.
- **Negativas RLS fallidas:** las dos cuentas profesionales obtuvieron HTTP 200 de Traslados y las tres tablas alimentarias directamente por REST. Se utilizó `select=id&limit=0`, sin descargar filas. Son ocho resultados que debían denegar y no denegaron. No se contabilizan como pruebas de seguridad aprobadas.
- El metadato remoto confirma RLS deshabilitado en esas cuatro tablas y sms_logs. Perfiles sigue sin RLS y con permisos amplios. No se ensayó una escritura destructiva de roles por REST para demostrar esta deficiencia.

La Fase B actual cubre perfiles y las dos tablas clínicas, **no resuelve por sí sola las tablas no clínicas**. No se declara segura toda Supabase.

## 8. Pruebas locales y evidencia

48 pruebas Python, 13 Node y 96 comprobaciones PostgreSQL aisladas aprobadas. Estas últimas usan Auth/JWT sintéticos y no acreditan Supabase Auth. La comprobación adicional de logout usa mocks con clave pública/JWT ordinario y respuesta 204 sin JSON.

Resultados reales separados: `output/eleven-real-auth-tests.json`, `output/eleven-real-browser.json`, `output/eleven-final-registry.json` y `output/eleven-phase-b-preflight.json`. El indicador `deployment_ready` de la prueba real permanece false por las negativas de base de datos fallidas.

## 9. Compatibilidad y decisión del corte

Los ocho perfiles históricos ya están conciliados; ese preflight dejó de bloquear B. No obstante, se detuvo el corte como pidió el titular ante incompatibilidades: activar RLS sólo en perfiles/clínicas y publicar el backend dejaría accesos directos indebidos en otras áreas. Hace falta diseñar/ensayar el delta de Traslados, Comidas y sms_logs con sus ownership, grants, operaciones permitidas y dependencias antes de aplicar cambios coordinados.

Los respaldos disponibles son las definiciones y metadatos afectados y el snapshot privado de roles administrativos; no equivalen a una restauración integral probada. Antes de otro corte debe conservarse un respaldo recuperable de su delta y un procedimiento de corrección hacia delante. Nunca restaurar automáticamente políticas públicas inseguras.

## 10. GitHub y Render

Se actualizó la referencia remota mediante fetch. `origin/main` continúa en 405ea50; `origin/feat/frontend-general` está en 5bf3201. Existe solapamiento de `core/formadig-core.js` entre seguridad y rediseño: la integración posterior debe conservar el UI del compañero y fusionar únicamente la lógica Auth necesaria. No se modificó su rama, HTML o CSS.

No se hizo push, merge, force push ni despliegue Render: la condición de publicación segura no se cumple. El backend de pruebas está en `http://127.0.0.1:8054`, ligado a loopback y conectado a Supabase real. Ese ensayo no demuestra que el login de Render esté actualizado ni que sus módulos ya funcionen. Las comprobaciones actuales de `/health` y `/api/status` agotaron el timeout de lectura de 15 segundos; no se certifica su disponibilidad ni se atribuye ese resultado a estos cambios locales.

## 11. Entrega privada

Contraseñas temporales reales: `C:\Users\Herna\AppData\Local\FORMADIG\security-activation\CREDENCIALES_SUPABASE_REALES.txt`.

Inventario individual: `C:\Users\Herna\AppData\Local\FORMADIG\security-activation\INVENTARIO_11_USUARIOS_VERIFICADOS.md`.

El directorio tiene ACL restringida al usuario de Windows. Existe un archivo privado JSON de credenciales para el ensayo; tampoco está en el repositorio. El archivo de demo anterior no contiene estas contraseñas y sus identidades .invalid siguen siendo sólo locales.

## 12. Pendientes exactos

1. Corregir y verificar los permisos directos de las tablas web restantes, preservando operaciones existentes y sin modificar código móvil ni atribuirle resultados.
2. Validar el delta con PostgreSQL aislado y JWT reales usando sólo registros ficticios autorizados; repetir las ocho negativas hoy fallidas.
3. Comprobar perfil/paciente y consumidores web, recuperar el esquema de forma segura ante un fallo y realizar el corte B/backend de manera coordinada.
4. Integrar la lógica Auth con el rediseño sin sobrescribirlo; entonces publicar y verificar el commit efectivo en Render, login, salud y módulos.
5. Si se requiere certificar login por contraseña de los ocho históricos, que su titular lo pruebe con las claves conservadas mediante un canal privado; no se restablecerán para facilitar el ensayo.

No falta aprobación individual de los ocho roles: ya fue recibida y ejecutada. **Las once identidades reales existen y sus roles están verificados; falta la activación segura completa de los módulos y la publicación.**
