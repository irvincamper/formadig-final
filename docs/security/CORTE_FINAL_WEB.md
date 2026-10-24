# Procedimiento del prompt final: sólo web

Este procedimiento está preparado, no ejecutado. No depende de móvil ni MongoDB. Supabase DIF y Render requieren la autorización del prompt final. A y contención ya están aplicadas y no se repiten.

## 1. Fijar versión y ventana

Trabajar en el worktree `codex/integracion-final-formadig`. Ejecutar `git fetch origin`, comprobar HEAD del PR y su diff final, que main todavía parte del commit esperado y que no haya nuevos cambios externos sin revisar. No usar reset ni force push. El PR debe mantenerse abierto sin auto-merge hasta autorizar el corte.

Render verificado en lectura: rama main, Auto-Deploy On Commit, PR Previews Off; build `pip install -r requirements.txt`; start `gunicorn run:app --workers 1 --threads 2 --worker-class gthread --timeout 30`; raíz del repositorio. El último despliegue comprobado es 405ea508bfd9db69b47f9813d89d1a7fe2f83316. No se cambió su configuración en el prompt preparatorio.

Render Free no dispone de mantenimiento nativo. La versión preparada admite `FORMADIG_MAINTENANCE=true`: devuelve 503 y Retry-After para web y API, permitiendo únicamente /health. El health incluye maintenance=true. La variable se evalúa al arrancar; cambiarla requiere reiniciar/desplegar. No basta establecerla en el backend antiguo.

En el prompt final: desactivar temporalmente Auto-Deploy, configurar mantenimiento y CLINICAL_ENABLE_UPDATES=false sin publicar secretos, e integrar el PR aprobado en main por merge commit (conservar historial). Desplegar exactamente ese commit con mantenimiento activo; comprobar /health y que /api/auth/me y /dashboard.html devuelven 503. Esto prepara un backend compatible sin abrir servicio antes del DDL. Si el despliegue falla, no ejecutar migraciones. Mantener durante la ventana la misma versión aprobada y no admitir otros merges.

## 2. Validar/refrescar respaldo privado

Binarios nativos disponibles: `%LOCALAPPDATA%\FORMADIG\tools\postgres17\runtime\pgsql\bin`, versión 17.11; servidor remoto 17.6. No se instaló un servicio de Windows ni se requiere Docker.

El respaldo probado está en `%LOCALAPPDATA%\FORMADIG\security-activation\backup-web01-final`. Contiene `security_schema.dump`, SQL legible, TOC, metadatos, manifest SHA-256 y restore-result.json; ACL local limitada al usuario. Su hash consta en el informe. No copiar esos archivos a Git ni al PR.

El alcance es el delta DDL: public, formadig_private, auth y extensions, incluyendo dependencias, funciones, triggers, políticas, grants y restricciones. No hay exportación de filas ni contraseñas de Auth. B/legacy no cambian registros; los datos existentes permanecen en DIF. No es un respaldo de datos completo ni sirve para recuperar registros borrados por otra operación. No ejecutar cambios de datos como parte del corte.

Antes del corte, si el estado cambió o pasó tiempo, generar una copia NUEVA (nunca sobrescribir el respaldo aprobado):

```powershell
$py='C:\Users\Herna\Downloads\PROYECTO INTEGRADOR\WEB\formadig-final\.venv-local\Scripts\python.exe'
$pg=Join-Path $env:LOCALAPPDATA 'FORMADIG\tools\postgres17\runtime\pgsql\bin'
$backup=Join-Path $env:LOCALAPPDATA 'FORMADIG\security-activation\backup-corte-final'
& $py -B scripts/backup_security_delta.py --pg-bin $pg --destination $backup
& $py -B scripts/verify_security_restore.py --pg-bin $pg --backup $backup
& $py -B scripts/prepare_web_cutover.py --backup $backup
```

Exigir salida exitosa, archivo no vacío, SHA idéntico al manifest y restore_test=passed. El ensayo usa un clúster NUEVO loopback, replica el DDL, compara tablas/ACL/RLS/políticas/FK, prueba B/legacy con identidades sintéticas, repetición abortada, 180 fixtures y limpieza, y fail_closed repetible. Nunca apunta a DIF para restaurar. Los roles plataforma locales son NOLOGIN y no se exportan sus contraseñas ni sesiones.

## 3. Preflight y ejecución por fases

Conservar en carpeta privada la salida de `npx --yes supabase migration list --linked` y de consultas de metadatos. Confirmar proyecto ctiqbycbkcftwuqgzxjb y que sólo A y contención figuren aplicadas. Revalidar once correspondencias Auth/perfiles/registro y distribución 3/4/2/1/1. Si cambia el esquema frente al snapshot restaurado, detener y revisar el delta; no ignorar el preflight ni marcar migraciones como aplicadas para saltarlo.

Los archivos preparados por prepare_web_cutover.py contienen SET de sesión seguido de la migración original completa. B y legacy incluyen BEGIN/COMMIT propios: no anidarlos en una transacción exterior ni usar SET LOCAL fuera de su transacción. Los settings son distintos y no sobreviven a conexiones distintas por sí solos.

Ejecutar únicamente después de autorizar este prompt final, con backend compatible confirmado en mantenimiento:

```powershell
$cut=Join-Path $backup 'cutover-prepared'
npx --yes supabase db query --linked --file (Join-Path $cut 'B.exec.sql')
if ($LASTEXITCODE -ne 0) { throw 'B falló: no ejecutar legacy ni abrir servicio' }
npx --yes supabase db query --linked --file supabase/tests/web01_post_cutover.sql
```

Después de B: perfiles RLS=true, anon sin SELECT, UPDATE de rol/id no concedido; clínica sólo SELECT para authenticated, sin INSERT/UPDATE/DELETE/TRUNCATE; políticas clínicas exigen rol confiable y atendido_por=auth.uid(), también para admin. Verificar las once correspondencias, cero inconsistencias y que no cambió el contenido de las tablas. Registrar B con CLI sólo después de comprobar SQL realmente aplicado:

```powershell
npx --yes supabase migration repair 20261023202914 --status applied --linked
npx --yes supabase db query --linked --file (Join-Path $cut 'legacy.exec.sql')
if ($LASTEXITCODE -ne 0) { throw 'legacy falló: mantener mantenimiento y evaluar contención' }
npx --yes supabase db query --linked --file supabase/tests/web01_post_cutover.sql
```

Después de legacy: nueve tablas con RLS activo; anon sin SELECT; ningún DELETE/TRUNCATE concedido a authenticated; soporte sólo área/propietario permitido y propietario inmutable; SMS sólo remitente autorizado; notificaciones propias, edición sólo leida e INSERT por trigger auditado. Confirmar función invocadora, search_path seguro y cuatro triggers. Ejecutar comprobaciones con filas WEB01 autorizadas y JWT del usuario, no service_role. Registrar legacy sólo al confirmar su éxito:

```powershell
npx --yes supabase migration repair 20261024012430 --status applied --linked
npx --yes supabase migration list --linked
```

No usar db push: la contención tiene una versión posterior a B y ya está aplicada. repair registra un hecho comprobado, no ejecuta la migración. Si se interrumpe el registro, inspeccionar políticas antes de reparar; no repetir archivos a ciegas. B y legacy NO son idempotentes; su repetición aborta y revierte la transacción de esa repetición, como se comprobó en aislamiento.

## 4. Fallos y recuperación

Ante fallo: no abrir servicio, no avanzar la fase ni publicar otro commit para disimular el error. Conservar salida privada y determinar si el COMMIT de la fase ocurrió. La respuesta segura preparada es ejecutar `supabase/recovery/formadig_fail_closed.sql` con CLI, después comprobar denegación en las nueve tablas. Es repetible y conserva filas, pero deja módulos fuera de servicio; no es restauración funcional.

El respaldo DDL se restauró por completo en una instancia aislada. Para una reconstrucción por desastre: restaurar primero en un destino nuevo aislado y validar dependencias de plataforma; después recuperar el delta revisado preservando datos existentes. No ejecutar pg_restore --clean contra DIF, no desactivar RLS ni reinstalar el esquema antiguo con permisos públicos inseguros. Un rollback que reabra esas políticas no cumple esta entrega; corregir el delta bajo mantenimiento y validar antes de reabrir.

## 5. Apertura y comprobación real

Introducir únicamente los fixtures explícitamente aprobados según DATOS_WEB01.md, mediante administrador SQL Editor. No crear beneficiarios reales ni identidades manuales. Mantener CLINICAL_ENABLE_UPDATES=false; no activar CLINICAL_SYNTHETIC_MODE, CLINICAL_ENABLE_CREATION ni repositorios falsos en Render. Los grants clínicos permanecen de consulta.

Tras comprobar B/legacy, cambiar FORMADIG_MAINTENANCE=false y reiniciar la MISMA versión aprobada. Verificar maintenance=false. Ejecutar login real de las tres cuentas nuevas, revalidación de sesión, menú, logout y denegaciones. Las otras ocho contraseñas no se restablecen; validar sus roles por metadatos y permisos SQL simulando claims sólo en transacciones de lectura, sin afirmar login por contraseña.

```powershell
& $py -B scripts/verify_web_cutover_real.py --after-cutover --base-url https://formadig-app.onrender.com
$env:FORMADIG_VALIDATION_URL='https://formadig-app.onrender.com'
$env:FORMADIG_BROWSER_REPORT='web-final-render-browser.json'
node scripts/verify_real_web_browser.cjs '<ruta local al paquete playwright>'
```

El primer script consulta exclusivamente id de los 180 UUID sintéticos; falla si faltan fixtures o una denegación no funciona. El navegador no debe descargar expedientes de terceros: sólo dashboard/identidad y consultas dirigidas a fixtures. Revisar web en escritorio y anchos 1024, 768 y 390; Gestión de Usuarios, soporte, clínica de consulta y perfil. Las búsquedas y segunda página clínica ya se probaron con mocks y se deben confirmar con WEB01 en el servicio desplegado. No enviar SMS reales.

Comprobar el SHA de `main` con `git ls-remote origin refs/heads/main`, el commit del merge del PR y el SHA Live del panel de Render; deben corresponder a la versión autorizada (un merge commit puede diferir del head de la rama). No declarar despliegue por /health únicamente. Tras aprobar el smoke, retirar sólo fixtures según cleanup y decidir si se restablece Auto-Deploy al valor original On Commit. Si falla el smoke, reactivar mantenimiento y contención; no abrir acceso inseguro.
