> Antecedente de la intervención anterior. Para el estado actual de la corrección local y su conservación en Git, consultar INFORME_SEGURIDAD_AUTENTICACION.md.

# FORMADIG — Integración main y Render

Fecha: 23 de octubre de 2026, America/Mexico_City.

## Dictamen

**NO APROBADO un nuevo push a main.** La versión visual ya estaba publicada al comenzar: origin/main y el servicio Render Live apuntan a `405ea508bfd9db69b47f9813d89d1a7fe2f83316`. Esta ejecución no realizó push, merge, despliegue manual, modificación de variables remotas, políticas ni registros. Las correcciones nuevas quedan en el árbol de desarrollo `feat/psicologia-dentista`, sin commit.

## 1. Causa raíz del error local

No existía `.env`; tampoco había variables SUPABASE_URL/SUPABASE_KEY en el proceso. run.py cargaba dotenv antes de importar los blueprints, por lo que el orden principal era correcto. Sin embargo, login_backend.py intentaba construir un cliente global con valores ausentes y lo dejaba en None. El mensaje posterior no identificaba la variable faltante. run.py advertía sobre service_role y no sobre la clave pública que el login necesita.

## 2. Correcciones

- Se creó `.env` exclusivamente desde `.env.example`, con la URL y clave publishable ya documentadas. Git confirma que está ignorado. No se incorporó ninguna clave privada.
- run.py carga el `.env` situado junto a él, conserva prioridad del entorno del proceso y muestra presencia de SUPABASE_KEY sin imprimir valores.
- Login crea un cliente independiente por solicitud, evitando compartir sesiones entre usuarios. Variables faltantes producen 503 con sus nombres; configuración inválida y errores del proveedor no exponen valores.
- Se rechaza una clave privilegiada en SUPABASE_KEY. No se usa service_role como sustituto.
- Se eliminó el fallback a user_metadata. Login exige app_metadata.role administrado y coincidente con perfiles. Una cuenta sin aprovisionamiento confiable recibe 403: esto puede bloquear cuentas antiguas y requiere preparación administrativa antes de desplegar.
- Se bloqueó `/api/auth/register` heredado con 403 porque asignaba roles por metadatos editables. Las altas legítimas deben pasar por Gestión de Usuarios verificada; no se crearon cuentas.
- Se añadieron siete pruebas de login. El mock de la prueba integrada se adaptó al cliente por solicitud y a app_metadata; no se debilitó la exigencia de autorización.

## 3. Validación

| Control | Resultado y alcance |
|---|---|
| Python unittest discover tests_clinical | 25/25: 18 existentes y 7 nuevas |
| Node test_frontend.cjs | 6/6 |
| Playwright visual_flow.js | 29/29, datos sintéticos en memoria |
| Playwright visual_fields.js | 7/7, Chromium 155 |
| JavaScript clinical-ui.js | node --check correcto |
| Blueprints | 11/11 registrados en Flask local y /api/status remoto |
| Contratos del diseño 405ea50 frente a su padre | Cinco archivos, tres CSS y dos HTML. Sin eliminación de id/name/action/href/src anteriores |
| git diff --check | Correcto |
| Supabase Auth settings con clave pública local | HTTP 200; confirma conectividad/configuración, no login |
| Login real | No probado; no se proporcionó cuenta de prueba autorizada |

El primer ensayo Python falló porque la prueba aún sustituía el cliente global eliminado. Se conservó su finalidad, actualizando la inyección y los claims confiables; la ejecución completa posterior aprobó. El RuntimeError registrado por la prueba negativa clínica es inducido para comprobar el manejo de errores. Una comprobación manual apuntó por error a clinical-data.js, que no existe; se identificó el archivo real clinical-ui.js y su comprobación aprobó.

Las capturas en output/playwright se regeneraron con datos ficticios. Las respuestas 400/403/503 del ensayo corresponden a negativas esperadas. No hubo errores JavaScript. Se bloquearon fuentes externas durante la demo, por lo que no acredita su disponibilidad ni su tipografía en producción.

## 4. Seguridad para publicación

Se revisaron INFORME_AUDITORIA_SUPABASE.md y PROPUESTA_RLS_REVISADA.md. La auditoría previa documenta SELECT/INSERT clínicos públicos permisivos, perfiles sin RLS y un trigger Auth que copia roles de metadatos editables. La propuesta revisada advierte dependencias con Gestión de Usuarios. Parte de sus descripciones de código quedó superada por los cambios de desarrollo; los hallazgos remotos no se consideran resueltos por esos cambios.

La consulta nueva a pg_policies mediante el conector Supabase fue denegada: `You do not have permission to perform this action`. Por tanto, el estado RLS actual no quedó revalidado y no se afirma que los hallazgos históricos sigan idénticos o hayan sido corregidos.

Restringir escrituras en Flask no corrige acceso directo a Data API ni protege lecturas clínicas. No se aprueba consulta clínica real hasta verificar permisos SELECT y protección de roles. La existencia de esos riesgos pendientes y la ausencia de prueba de compatibilidad con roles administrados impiden un nuevo despliegue aprobado.

Se mantuvo CLINICAL_ENABLE_UPDATES=false local. En Render no aparece esa variable entre las siete variables del servicio; el código del commit Live usa false por defecto cuando está ausente. La creación real exige simultáneamente modo sintético y bandera de creación en configuración Flask; run.py no los habilita. No se hicieron POST/PATCH clínicos en producción. Estas comprobaciones son del bloqueo de aplicación, no certificación RLS.

## 5. Referencias Git

- main local: `c74e6f7ac2337ab8e12441a94a275f2977602a4e`.
- Rama clínica / HEAD inicial: `405ea508bfd9db69b47f9813d89d1a7fe2f83316`.
- origin/main después de fetch y git ls-remote: `405ea508bfd9db69b47f9813d89d1a7fe2f83316`.
- origin/feat/psicologia-dentista: `a9be3929edc9656dd9f72c86eb6cb3e2b5c0d7bb`; rama local inicialmente un commit por delante.
- Diseño del compañero: 405ea50, cinco archivos visuales presentes.

El árbol estaba limpio al inicio. No se movió main local: sigue conservando la referencia previa recuperable. No se reescribió historial ni se eliminaron ramas. Los cambios fuente, pruebas, informe y capturas de esta revisión permanecen sin commit en desarrollo.

## 6. Push

No se realizó. La publicación visual en origin/main fue encontrada, no ejecutada por esta revisión. Las correcciones de login descritas aquí todavía no están en GitHub ni Render.

## 7. Render verificado

Panel autenticado del servicio srv-d7cuee1j2pic73f81v20:

- Repositorio irvincamper/formadig-final, rama main.
- Último despliegue exitoso Live: 405ea508bfd9db69b47f9813d89d1a7fe2f83316.
- Trigger del despliegue: Auto-Deploy; duración mostrada 1m52s.
- Deploy: dep-dbdrt3ks728c7383ur1g.
- SUPABASE_URL, SUPABASE_KEY y SUPABASE_SERVICE_ROLE_KEY definidas; valores no revelados ni modificados. Su presencia no prueba validez de todas ellas.
- /health: HTTP 200; /api/status: HTTP 200, 11 blueprints.
- Páginas HTML de Psicología y Dentista: HTTP 200.

Se verificó el resultado del despliegue y el servicio en ejecución. No se revisó el log completo del build/arranque ni se ensayó login real; no se certifica ausencia de todos los errores operativos. El éxito técnico de ese despliegue no constituye aprobación de seguridad clínica.

## 8. Módulos existentes

Transporte, desayunos fríos, desayunos calientes, espacios EAEyD y Gestión de Usuarios sirven sus páginas HTML con HTTP 200 en Render. Los blueprints previos siguen registrados y Node comprueba continuidad de sidebar. Los tests sintéticos ejercitan permisos de Gestión de Usuarios y roles clínicos. No se modificó la aplicación móvil.

No hay evidencia suficiente para afirmar regresión funcional real superada de Transporte/Comidas/Gestión de Usuarios: faltan cuentas autorizadas, operaciones ficticias controladas y verificación de proveedores. No se hicieron cambios remotos para conseguir resultados positivos.

## 9. Psicología y Dentista

Diseño presente en main remoto y servido por Render. Listados, búsqueda, detalle, formularios, validaciones, edición, paginación, menú por rol, errores, cierre de sesión y controles estrechos aprobados exclusivamente en demo sintética local. No hay prueba de persistencia PostgreSQL ni atenciones reales.

## 10. Pendientes que bloquean publicar la corrección

1. Obtener acceso de lectura a metadatos RLS y verificar exposición/grants/políticas reales.
2. Autorizar específicamente y preparar la corrección coordinada de perfiles, trigger y políticas clínicas, sin desactivar RLS ni eludirlo con service_role.
3. Aprovisionar roles app_metadata legítimos y contrastarlos con perfiles; no promover automáticamente user_metadata.
4. Probar con cuentas autorizadas positivas y negativas por rol, incluida autoelevación y acceso directo por REST.
5. Validar regresión funcional de módulos existentes y altas administrativas con datos ficticios autorizados.
6. Revisar el diff de desarrollo, repetir controles sobre el commit final y sólo entonces integrar/publicar. Verificar Render y su SHA después.

## 11. Próximo trabajo frontend

Consultar GUIA_FRONTEND_GENERAL.md. El compañero puede basar su diseño en origin/main, que ya contiene 405ea50, pero las correcciones locales de esta revisión aún no forman parte de esa base. Todo PR debe pasar revisión funcional y seguridad antes de fusionarse; Auto-Deploy publica main automáticamente.

Referencias: documentación oficial de Supabase RLS, https://supabase.com/docs/guides/database/postgres/row-level-security; contratos locales en CONTRATO_FRONTEND.md. La documentación no sustituye comprobaciones de políticas del proyecto.
