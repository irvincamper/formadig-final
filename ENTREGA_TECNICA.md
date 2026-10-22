# FORMADIG — entrega técnica local

Consolidación: 22 de octubre de 2026. Rama `feat/psicologia-dentista`, base c74e6f7. Commit local autorizado; **sin push, merge ni despliegue**. Este documento es el punto de entrada de la entrega. El hash definitivo se consulta con `git log -1 --oneline` y se entrega al titular, para no introducir una referencia circular dentro del propio commit.

## Qué incorpora la rama

- Módulos Psicología y Dentista en la estructura existente logica/vistas/diseno, con adaptación de formularios/listados y sin rediseño visual definitivo.
- Servicios compartidos clinical: validaciones de campos/filtros, repositorio REST con clave pública y JWT por petición, autorización por identidad y app_metadata.role consistente con perfiles.rol. No se usan claves privilegiadas para expedientes.
- Blueprints registrados en run.py, login único, dashboard y sidebar. Roles web canónicos psicologo/dentista; admin accede a ambas áreas. Transporte/Comida conservan sus reglas y módulos.
- Gestión de Usuarios: tipos profesionales, alta Auth administrativa sólo en backend, cliente de tablas por sesión del solicitante; cambios de rol que requieren coordinación Auth/perfil continúan bloqueados.
- Listado, búsqueda, filtros, detalle, historial y paginación; registro y edición sólo ensayados con datos ficticios. CLINICAL_ENABLE_UPDATES=false en configuración de ejemplo; sin DELETE clínico ni tablas nuevas.
- Pruebas unitarias, demo sintética, funciones de automatización Playwright, informes y capturas exclusivamente sintéticas.

## Archivos para incorporar a GitHub cuando el titular autorice push

| Grupo | Contenido |
|---|---|
| Módulos | Ocho archivos: backend, JS de arranque, HTML y CSS de admin_psicologia y admin_dentista |
| Servicios | clinical/__init__.py, api.py, repository.py, validation.py |
| UI compartida | core/clinical-ui.js, css/clinical.css, core/formadig-core.js, dashboard.html |
| Integración existente | run.py; JS/backend de login; JS/backend/HTML de admin_usuarios; .env.example |
| Pruebas | Nueve archivos fuente en tests_clinical, incluidos fakes, demo, suites Python/Node y funciones Playwright |
| Evidencia compartible | output/playwright: capturas de pacientes ficticios y resultados JSON; sin trazas, cookies, credenciales ni capturas del panel Supabase |
| Documentación | Esta guía, CONTRATO_FRONTEND.md, informes de adaptación/implementación/validación/auditoría/integración, matriz y propuestas RLS; DATOS_PRUEBA_CLINICOS.sql sólo como script preparado, NO ejecutado |
| Higiene | .gitignore y retirada del índice de entornos/cachés antes versionados; no se borran del equipo |

La lista exacta del commit se obtiene con `git show --name-status --format=short HEAD`. Los documentos históricos se conservan con sus notas de fase; para el contrato actual prevalecen esta guía y CONTRATO_FRONTEND.md. Que un informe histórico diga sin commit describe su fase, no una prohibición vigente: el titular autorizó este commit de consolidación.

## Exclusiones y conservación

Se retiraron **sólo del índice Git** los entornos .venv/ y Formadig/.venv/ (4922 archivos cada uno) y once cachés .pyc fuera de ellos: 9855 artefactos en total. Permanecen físicamente en sus rutas y son recuperables además desde la historia Git. .venv-local también se conserva e ignora. No usar esos entornos heredados para reproducir la entrega.

.gitignore excluye entornos, __pycache__, pyc, node_modules, logs, temporales, artefactos internos Playwright, .env privados y formatos de claves/certificados privados. .env.example se incluye porque contiene sólo configuración pública y el bloqueo de seguimiento; una publishable key no es service_role ni una credencial administrativa. No introducir secretos allí.

evidencias_supabase/ queda **local y excluido**: respaldo técnico y capturas de la cuenta remota. Los informes pueden mencionarlo como antecedente privado; esos archivos no se entregan al compañero ni son necesarios para diseñar. No se borraron. Las imágenes compartidas de output/playwright se revisaron en la fase visual y usan únicamente Cuenta sintética/Paciente sintético, UUID ficticios y notas de prueba.

La revisión de secretos se limita a los archivos agregados/modificados de esta entrega y a la exclusión de rutas sensibles; no se reescribe ni se certifica el historial previo completo. La retirada de entornos en el nuevo commit no reduce por sí sola el tamaño de commits antiguos. No se ejecutó una purga del repositorio.

## Para el desarrollador frontend

Leer [CONTRATO_FRONTEND.md](CONTRATO_FRONTEND.md) antes de editar. Ahí están las cinco rutas editables, los IDs/names/tipos de campos, la estructura de respuesta, los límites y las restricciones de permisos. Trabajar principalmente en los dos HTML y sus dos CSS específicos; clinical.css es compartido y requiere revisar ambas vistas. No tocar servicios Python, autenticación, roles, SQL ni JavaScript compartido para resolver una cuestión visual.

Conservar los anclajes del DOM, scripts externos/defer, endpoints, capacidades, tratamiento de datos como texto, fechas UTC y decimales. El sidebar sólo orienta navegación: nunca sustituye la autorización del servidor. No habilitar controles ignorando capacidades ni convertir la demo en aplicación conectada.

Después de que el titular publique la rama, el compañero podrá obtenerla desde origin y seleccionar feat/psicologia-dentista; hasta entonces esta entrega es sólo local. No se ha creado PR ni se ha fusionado con main. No abrir una demo en red pública.

## Preparación en otro equipo y ensayo sin Supabase

Usar Python 3.11 instalado y crear un entorno propio desde la raíz. El alias del lanzador puede variar según la instalación:

```powershell
py -3.11 -m venv .venv-local
& ./.venv-local/Scripts/python.exe -m pip install -r requirements.txt
& ./.venv-local/Scripts/python.exe -B -m tests_clinical.serve_synthetic --enable-creation --enable-updates
```

Abrir http://127.0.0.1:8011/demo y seleccionar Admin/Psicólogo/Dentista. No se necesitan .env ni claves privadas para esta demo. Los dos indicadores habilitan sólo el repositorio falso en memoria, no Supabase. Al detener el proceso se pierden los datos. Detenerlo al terminar. Los permisos reales y sus flags no se cambian.

requirements.txt heredado no fija todas las versiones; no se actualizó ni se inventó un lockfile en esta consolidación. La prueba de instalación desde cero en otro equipo queda pendiente; crear un lockfile reproducible debe revisarse aparte antes de una entrega desplegable.

## Verificaciones de la consolidación

Ejecutadas nuevamente el 22 de octubre de 2026:

```powershell
& ./.venv-local/Scripts/python.exe -B -m unittest discover -s tests_clinical -p 'test_*.py'
node --test tests_clinical/test_frontend.cjs
git diff --check
git diff --cached --check
```

Resultado: 18 pruebas Python y 6 Node aprobadas. Cubren blueprints, rutas, login mockeado, roles nuevos y denegaciones, navegación, contratos HTML/serialización, alta y edición sintéticas, filtros y manejo de errores. Los mensajes de éxito de Auth del ensayo son mocks, no altas reales. Las advertencias de deprecación del SDK y el error simulado del test negativo están documentados; no se ocultó ningún fallo.

La evidencia visual previa del mismo día contiene **36/36 comprobaciones de navegador aprobadas**, conservadas y verificadas en sus JSON; no se repitió la sesión completa de navegador en esta consolidación, que sólo cambió higiene/documentación y un comentario del login. Ver [INFORME_VALIDACION_VISUAL.md](INFORME_VALIDACION_VISUAL.md). El servidor de demo permanece detenido.

Revisión del índice antes del commit: 58 archivos agregados/modificados y 9855 retiradas exclusivamente de artefactos; ninguna retirada de código funcional. Escaneo de los contenidos preparados sin patrones detectados de claves privadas, claves secretas Supabase, JWT literales, claves AWS ni URL PostgreSQL con contraseña. Las capturas son PNG sintéticos revisados visualmente, no texto inspeccionable por ese escáner. Esta comprobación no equivale a una auditoría exhaustiva del historial.

## Pendientes de integración real

1. Diseñar/aprobar y probar RLS de lectura/UPDATE y privilegios mínimos; no aplicar las propuestas por copiar un documento histórico.
2. Aprovisionar cuentas reales autorizadas con claims confiables; no migrar roles desde metadatos editables.
3. Coordinar cambios de rol entre Auth y perfiles, y compatibilidad del backend desplegado antes de endurecer permisos compartidos.
4. Crear fixtures sólo cuando se autorice su ejecución y se verifiquen todas las FK/dependencias del script; actualmente no se ejecutó.
5. Probar JWT ordinarios, denegaciones directas y persistencia PostgreSQL, además de la UI; no usar service_role para expedientes.
6. Regresión funcional de servicios antiguos reales y revisión del diseño definitivo, otros navegadores y dispositivos.

No se modificó Supabase, Render, aplicación móvil ni main. No se habilitaron escrituras clínicas reales. Preparada para compartir como **rama de desarrollo local**, pendiente de autorización de push; no es una versión desplegada.
