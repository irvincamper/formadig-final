# Cierre técnico FORMADIG Web — Prompt 1

Fecha local: 23 de octubre de 2026. Alcance definitivo: exclusivamente web. Móvil y MongoDB no son dependencias de publicación.

## 1. Aplicación web

La versión integrada está preparada para el corte autorizado en el próximo prompt. Conserva Flask, los contratos HTML/JS y la identidad verificada con Supabase Auth. Esta intervención no aplicó B/legacy ni realizó despliegues. Los accesos legacy inseguros siguen pendientes en DIF; no se declara resuelta la seguridad remota.

## 2. Frontend y backend

Se conservó la integración existente b86ce7b y los merges 26c5776 y 4ec5500; no se repitió la integración del rediseño. La presentación de core/formadig-core.js sigue combinada con revalidación Auth, rol y logout. No se modificó el diseño en esta intervención. Se amplió la validación responsive a 1365, 1024, 768 y 390 píxeles.

Se añadió FORMADIG_MAINTENANCE al backend porque Render Free no permite mantenimiento nativo: bloquea web/API con 503 y Retry-After y conserva /health con indicador maintenance. Permite desplegar la versión compatible cerrada antes del DDL y abrirla tras verificarlo. Está desactivado por defecto y fue probado.

## 3. Las once cuentas

Consulta remota actual: admin=3, admin_traslados=4, admin_desayunos=2, psicologo=1, dentista=1. Las once coinciden entre Auth, perfiles y registro protegido; inconsistencias=0. No se crearon usuarios, no se cambiaron roles ni contraseñas. Las tres cuentas nuevas aprobaron nuevamente su login real en el backend final local (8056), dashboard, menú, rechazo del rol local falsificado, logout y token inválido. No se afirma login por contraseña de las ocho históricas.

## 4. Pruebas finales

| Prueba | Resultado | Naturaleza |
| --- | --- | --- |
| Python unittest | 50 aprobadas | Mocks backend; incluye mantenimiento |
| Node | 13 aprobadas | Contratos Auth/frontend |
| PostgreSQL 17 aislado | 274 comprobaciones aprobadas | Filas sintéticas, RLS, grants, triggers y contención |
| Restauración DDL real | Aprobada | Clúster nuevo loopback; sin filas reales |
| B/legacy sobre DDL restaurado | Aprobadas | Once identidades sintéticas; no producción |
| Seed y limpieza WEB01 | 180 filas; aprobados | Sólo laboratorio; repetición seed aborta sin sobrescribir |
| Playwright cinco roles | 23 combinaciones aprobadas | Datos/Auth simulados; cuatro resoluciones |
| Búsqueda/paginación/error clínico | Aprobadas | Páginas 25+5, vacío, error 503 y recuperación con fixtures |
| Auth real con navegador | 3 cuentas aprobadas | Auth DIF y Flask local; sin expedientes |

Evidencias públicas sin inventarios nominales: output/web01-python.txt, web01-node.txt, web01-rls.json, web01-backup-restore.json, final-integrated-ui.json, web01-real-browser.json y web01-remote-preflight.json. Un ensayo adicional de error confundió el texto mostrado en mayúsculas por CSS con el texto DOM; se corrigió el lector del test a textContent conservando la aserción sobre el mensaje exacto. La evidencia inicial se conserva separadamente.

Las pruebas con mocks no prueban persistencia remota. El laboratorio aplica SQL real con auth.uid/auth.jwt simulados. Las nuevas políticas remotas siguen sin aplicar, por lo que sus pruebas PostgREST reales se reservan al corte. /health no se usa como prueba de seguridad.

## 5. Respaldo y restauración comprobados

Se resolvió la dependencia de Docker mediante pg_dump/pg_restore nativos 17.11, procedentes de los binarios oficiales EDB enlazados por PostgreSQL. El servidor DIF es 17.6; los binarios 16 instalados no eran la opción compatible. No se instaló Docker ni un servicio PostgreSQL nuevo.

Respaldo privado fuera del repositorio: `%LOCALAPPDATA%\FORMADIG\security-activation\backup-web01-final`. Archivo custom security_schema.dump: 167120 bytes. SHA-256:

`b88d4004e62b290acce835b8b4fb539ba0b1ab2313723253d363ce222e22e8fa`

La carpeta tiene ACL restringida al usuario. Incluye SQL, TOC, snapshot de metadatos, manifest e informe de restauración. Se utilizó la conexión temporal oficial obtenida por Supabase CLI, SSL y modo de sólo lectura; pg_dump adopta el rol postgres como el script oficial de CLI. No se utilizó service_role para leer tablas.

El alcance es recuperación del delta DDL autorizado: esquemas public/formadig_private, dependencias auth/extensions, tablas, funciones, triggers, índices, restricciones, RLS y ACL. No exporta filas clínicas, perfiles, credenciales, sesiones ni contraseñas de Auth. B/legacy no alteran filas y por eso su reversión no requiere exportarlas. NO es un respaldo integral de datos del proyecto ni permite recuperar datos borrados por otras operaciones.

La restauración completa de ese DDL en PostgreSQL 17 aislado terminó sin errores. Tablas/ACL/RLS, políticas y restricciones coinciden con el snapshot remoto. En el esquema restaurado se aplicaron las dos fases, se probó que repetirlas aborta, se insertaron/retiraron los 180 fixtures y se ejecutó fail_closed dos veces. No se restauró nada sobre DIF. fail_closed sigue siendo contención, no recuperación funcional; el dump sí se restauró de manera independiente.

Durante la preparación se diagnosticaron permisos de la conexión temporal (SET ROLE explícito de pg_dump), UTF-8 del comparador y herencia de pipes de pg_ctl en Windows. Las ejecuciones fallidas y sus logs privados se conservaron; los archivos vacíos anteriores no se consideran respaldos.

## 6. Migraciones B y legacy

A 20261023202836 y contención 20261023214516 continúan aplicadas, sin repetición. B 20261023202914 y legacy 20261024012430 siguen pendientes. No se reescribió su SQL porque aprobaron contra el DDL remoto restaurado.

Orden preparado: B y después legacy, con aplicación compatible en mantenimiento. Cada archivo tiene BEGIN/COMMIT y gate de sesión propio. prepare_web_cutover.py genera dos wrappers privados con SET de sesión antes del archivo completo y un manifest de hashes. Sólo prepara; no conecta ni ejecuta. No usar SET LOCAL fuera de las transacciones ni envolver ambos archivos en una transacción exterior.

No son idempotentes: la segunda ejecución aborta con rollback de esa repetición. El historial oficial debe registrarse únicamente después de verificar la fase realmente ejecutada. No usar db push indiscriminado: contención tiene un timestamp posterior a B y ya está aplicada.

## 7. Seguridad y RLS

El fingerprint remoto legacy sigue siendo 8b2d058184e6f68f055d512419a78345, igual al preflight revisado. No aparecieron dependencias incompatibles en la restauración. Los permisos se basan en registro protegido, app_metadata administrado y JWT verificado, nunca user_metadata, LocalStorage o encabezados de rol.

B limita perfiles y lectura clínica por área/asignación. Incluso admin necesita estar asignado a una atención para consultarla. Legacy protege soporte, SMS y notificaciones con operaciones y propietarios controlados; conserva las tablas y sus estructuras. Los triggers de notificación invocadores se probaron con filas. No se conceden escrituras clínicas. No se certifican consumidores externos fuera del alcance web, pero su ausencia ya no bloquea esta entrega.

## 8. Datos sintéticos preparados

supabase/tests/web01_seed.sql y web01_cleanup.sql contienen gates y UUID exactos, marcadores y propietarios. No hay inserciones en auth.users ni cambios de perfiles/roles. La guía docs/security/DATOS_WEB01.md indica cómo seleccionar las tres cuentas nuevas, respetar FK, retirar sólo fixtures y evitar notificaciones/SMS colaterales.

Los 180 registros se probaron sólo en aislamiento. El paciente técnico de los fixtures es la cuenta admin NUEVA de prueba; el motivo es explícitamente ficticio, sin historia médica de una persona. La inserción administrativa de esos fixtures en DIF requiere la decisión del último prompt y no activa escrituras desde la web.

## 9. Publicación de la rama

Se autoriza únicamente codex/integracion-final-formadig. La revisión de TODOS los blobs salientes detectó correos de cuentas en un informe histórico. Se conserva el historial original localmente y se anonimiza ese contenido en la copia destinada a GitHub antes del push, sin volver a integrar ni cambiar la implementación. El escaneo también compara las contraseñas actuales y secretos locales; las claves públicas publishable/anon se distinguen de claves privadas.

El estado definitivo de publicación y PR se registra al cerrar esta intervención. No se publican .env, respaldos, inventarios privados, contraseñas, tokens, capturas reales ni archivos temporales. Las evidencias no versionadas se conservan fuera del árbol de publicación.

## 10. Pull Request

Base main; compare codex/integracion-final-formadig. Enlace de comparación: https://github.com/irvincamper/formadig-final/compare/main...codex/integracion-final-formadig . El PR se crea sin merge ni auto-merge; su URL definitiva se incorpora al finalizar.

## 11. Commits

Base remota: 405ea508bfd9db69b47f9813d89d1a7fe2f83316. Rediseño integrado: 5bf320100af50a88b32567ee6064e53cef8dcacd. Integración funcional local anterior: b86ce7b. Los commits originales permanecen recuperables localmente; la anonimización para publicar cambia los SHA descendientes del informe saneado. El commit técnico y el head publicado se registran tras verificar push/PR.

## 12. Render sin cambios

Se consultó su panel en lectura: servicio srv-d7cuee1j2pic73f81v20, rama main, Auto-Deploy On Commit, PR Previews Off y último Live 405ea508bfd9db69b47f9813d89d1a7fe2f83316. No se cambió configuración, no se disparó deploy ni se fusionó main. El push de la rama y el PR no despliegan este servicio con esa configuración.

## 13. Procedimiento exacto

docs/security/CORTE_FINAL_WEB.md contiene comandos y condiciones por fase: fijar commit, refrescar/verificar respaldo, mantenimiento compatible, B, comprobar/registrar historial, legacy, comprobar/registrar historial, fixtures, smoke real, apertura del mismo commit y comprobación SHA GitHub/Render. Incluye actuación ante fallos y distingue contención de restauración DDL. supabase/tests/web01_post_cutover.sql inspecciona metadatos y roles; scripts/verify_web_cutover_real.py está preparado para SELECT id de fixtures con JWT real, sin usar service_role.

La publicación final no depende de móvil ni MongoDB. No hay que recrear usuarios ni repetir aprovisionamiento. Las escrituras clínicas deben permanecer bloqueadas y las nuevas políticas deben comprobarse realmente después del corte, antes de declarar éxito productivo.

## 14. Dictamen

Preparación técnica web completada con respaldo DDL restaurado, migraciones probadas sobre esquema real restaurado, datos ficticios verificables y suites aprobadas. No quedan bloqueos técnicos por Docker o ausencia de código móvil. El corte B/legacy, la fusión a main y el despliegue siguen reservados al prompt final, junto con las verificaciones reales posteriores.

**LISTO PARA PROMPT FINAL DE PUBLICACIÓN**

Referencias de herramientas: [respaldo/restauración oficial Supabase](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore), [binarios PostgreSQL para Windows](https://www.postgresql.org/download/windows/), [descarga oficial EDB](https://www.enterprisedb.com/download-postgresql-binaries).
