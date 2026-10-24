# FORMADIG — Usuarios de prueba

23 de octubre de 2026. **Tres cuentas funcionales de DEMOSTRACIÓN LOCAL. No son cuentas Supabase y NO funcionan en Render.**

## 1. Roles disponibles

Python define cinco roles web: admin, admin_traslados, admin_desayunos, psicologo y dentista. Las migraciones preparan un registro confiable para esos mismos valores; están sin aplicar en DIF. No se creó otro rol administrador ni se inventaron roles móviles.

## 2. Cuentas verificadas

| Correo exclusivo de demo | Rol | Entorno |
|---|---|---|
| admin@formadig.example.invalid | admin | localhost:8053 |
| psicologo@formadig.example.invalid | psicologo | localhost:8053 |
| dentista@formadig.example.invalid | dentista | localhost:8053 |

Son identificadores reservados .invalid, no buzones de correo reales. Cada identidad tiene UUID local distinto y contraseña temporal aleatoria diferente. Se conservan localmente; repetir el arranque no crea tres cuentas nuevas.

Los informes anteriores documentan fixtures y simulaciones, no altas reales. La consulta agregada de cuentas explícitamente marcadas para prueba en DIF mediante MCP fue denegada por permisos. No se enumeraron cuentas, no se leyeron datos personales ni contraseñas. **No se pudo establecer si existen cuentas reales autorizadas equivalentes; no se afirma que no existan.**

## 3. Cuentas creadas

Se prepararon exactamente tres identidades locales. No se crearon cuentas administrativas o profesionales en DIF: sus riesgos de políticas/trigger siguen pendientes y no hay un entorno alternativo autorizado. No se aplicaron migraciones para facilitar un registro.

La demo usa un proveedor Auth simulado en memoria con contraseñas almacenadas como hash para el servidor, tokens aleatorios con expiración y revocación al cerrar sesión. Los textos de contraseña sólo están en la salida privada local para el titular, fuera del repositorio. Ningún informe, captura o salida de pruebas incluye las contraseñas temporales generadas.

## 4. Relación Auth, perfiles y roles

En demo, los adaptadores devuelven identidad, UUID y app_metadata.role coherentes con un perfil sintético. No existe escritura PostgreSQL ni cliente Supabase real. La consulta clínica está sembrada sólo con registros ficticios y las escrituras están bloqueadas.

En Supabase real, hace falta Auth Admin autorizado, trigger seguro, perfil vinculado y registro privado de roles. El alta preparada verifica de nuevo Auth y perfil; un rol escrito únicamente en perfiles no concede autorización. Ver docs/security/ACTIVAR_CUENTAS_PROFESIONALES.md.

## 5. Pruebas

- 47 pruebas Python, 12 Node y 92 comprobaciones PostgreSQL aisladas aprobadas.
- Navegador Chrome: las tres cuentas iniciaron sesión con el formulario real de login y sus contraseñas temporales locales; se comprobó rol, dashboard, menú, siete endpoints de áreas y revocación al cerrar sesión. Token inválido rechazado.
- Admin: lectura permitida de Traslados, tres módulos alimentarios, Psicología, Dentista y Gestión de Usuarios. Psicologo: sólo Psicología entre esas áreas. Dentista: sólo Dentista. Endpoints administrativos de demo simulan listados; no acreditan persistencia ni funciones reales de esos módulos.
- Los permisos del backend web real se ensayan adicionalmente con mocks en tests_clinical/test_web_security.py. La demo no sustituye esas pruebas ni demuestra RLS productivo.
- No hay prueba de Supabase Auth real, persistencia remota ni acceso real a pacientes. No hubo envío SMS, llamadas Gemini, cambios en Render ni push.

Evidencia sin secretos: output/demo-users-browser.json y output/preproduction-rls-web.json. El navegador de pruebas bloqueó solicitudes externas; la demo también aplica CSP connect-src self para impedir conexiones a Supabase/Render. No se grabaron trazas ni capturas de credenciales.

## 6. Bloqueos pendientes

Faltan aprobación/aplicación coordinada de RLS y trigger, aprovisionamiento de cuentas aprobado, correos controlados, comprobación Auth/PostgREST real y regresión funcional sobre el entorno autorizado. La seguridad remota no se considera resuelta. Móvil queda fuera del alcance y sus roles existentes no se modificaron.

## 7. Inicio de sesión

Abrir http://127.0.0.1:8053/ y usar los identificadores de demo anteriores. Las contraseñas se entregan una sola vez en el panel local privado; no se copian al chat ni a este informe. Cambiar o regenerar las temporales después del ensayo mediante un procedimiento local autorizado. La demo debe permanecer ligada a 127.0.0.1, sin túneles ni publicación.

El proceso local se mantiene abierto para probarlo; al detenerlo se pierden sesiones y registros en memoria, no las tres identidades locales. Los archivos privados están bajo LOCALAPPDATA/FORMADIG/demo-web-accounts con permisos restringidos al usuario de Windows. Para reiniciar: ejecutar Python de .venv-local con `-B -m tests_clinical.account_demo --accounts` y la ruta privada accounts.json, puerto 8053; no imprimir ni copiar credentials.private.json. Los accesos a este servidor no funcionan en https://formadig-app.onrender.com.

Para Render sólo procederá entregar credenciales después de crear/verificar cuentas mediante el procedimiento seguro y autorización específica. Hoy no existen contraseñas reales creadas por esta intervención que puedan entregarse para Render.
