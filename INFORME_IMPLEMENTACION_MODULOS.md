# FORMADIG: implementación funcional local de Psicología y Dentista

Actualización: consultar INFORME_ADAPTACION_MODULOS.md y CONTRATO_FRONTEND.md para el contrato local vigente: roles psicologo/dentista, claims confiables y registro exclusivamente sintético. El contenido siguiente es antecedente histórico; sus nombres de roles y reglas de creación no prevalecen sobre el adjunto más reciente.

21 de octubre de 2026. Rama `feat/psicologia-dentista`, basada en c74e6f7. Cambios sin commit ni push. No se modificó main, Render ni la base productiva.

## Alcance final acordado

Las solicitudes se crean en la app móvil. La web consulta las solicitudes y actualiza el seguimiento. Se retiró la creación clínica web del primer borrador al aclararse este flujo. No hay botón de nueva atención, POST clínico funcional ni eliminación. El esquema no contiene una columna de aprobación dental; no se inventó un flujo de aceptar/rechazar que requiera campos inexistentes.

Se siguieron las convenciones del frontend estático publicado y la referencia de Traslados: encabezado/menú comunes, listado a la derecha y expediente seleccionado a la izquierda en escritorio, apilado en pantalla pequeña. El diseño final queda a cargo del otro desarrollador.

Roles incorporados al código por autorización explícita del usuario: `admin_psicologia` y `admin_dentista`. Se conserva un solo login. Admin General ve las cuatro áreas (Traslados, Comidas con sus tres submódulos, Psicología y Dentista); cada responsable clínico ve su área. Los dos tipos aparecen en el selector de altas y el listado administrativo. No se crearon cuentas reales ni contraseñas.

## Arquitectura

- `clinical/api.py`: fábrica de blueprints, verificación Auth/perfil, autorización por área, capacidades, listado, detalle, historial y PATCH de seguimiento. POST devuelve 405 con instrucción de usar la móvil. No existe DELETE.
- `clinical/repository.py`: adaptador REST Supabase con clave pública y JWT del solicitante por llamada, timeout, errores saneados, filtros en servidor, paginación y return=representation. Sin cliente global con sesión mutable ni fallback service_role. La expansión de paciente obtiene sólo nombre_completo por la FK auditada y la UI usa UUID si no está disponible.
- `clinical/validation.py`: UUID, fechas con zona y rango, textos obligatorios/longitudes, números de sesión, decimales/costos y filtros. Rechazo de operadores de búsqueda, campos desconocidos y reasignación de paciente/ID/profesional.
- `admin_psicologia` y `admin_dentista`: estructura logica/vistas/diseno, adaptadores de blueprint y scripts de inicio pequeños.
- `core/clinical-ui.js`: búsqueda, paginación, historial, carga de detalle y seguimiento parcial. No envía POST de alta. Preserva fechas históricas y campos sin cambios. Sin autorización basada en frontend.

Se usan tablas/columnas verificadas en `INFORME_AUDITORIA_SUPABASE.md`; no se hicieron cambios de esquema. No se agregaron dependencias Python o npm. Los nuevos servicios sólo requieren Flask y requests ya instalados.

## Archivos existentes modificados

| Archivo | Cambio |
|---|---|
| run.py | Dos blueprints adicionales; total 11. Salida Unicode compatible con PowerShell/Windows |
| .env.example | CLINICAL_ENABLE_UPDATES=false, sin secretos añadidos |
| core/formadig-core.js | Enlaces y separación de áreas por rol, conservando menú común |
| dashboard.html | Tarjetas de Psicología/Dentista según rol |
| modulos/login/logica/login.js | Documenta login único; retira mapa de redirección no utilizado |
| modulos/login/logica/login_backend.py | Autorizar registro administrativo por perfil verificado sin fallback a user_metadata; importa datetime usado por ese flujo |
| modulos/admin_usuarios/logica/admin_usuarios_backend.py | Admite dos tipos nuevos, guard de administración en servidor y 503 explícito si el proveedor administrativo Auth no está configurado |
| modulos/admin_usuarios/logica/admin_usuarios.js | Roles y etiquetas de las dos áreas nuevas |
| modulos/admin_usuarios/vistas/admin_usuarios.html | Dos opciones de rol nuevas |

Archivos nuevos: paquete clinical (4 archivos), módulos nuevos (backend, JS, HTML y CSS por módulo), core/clinical-ui.js, css/clinical.css, tests_clinical (fakes, unittest, pruebas Node y servidor sintético), y estos tres entregables: informe, contrato frontend y propuesta RLS. El informe de auditoría previo se conservó sin alteración.

## Seguridad y permisos

Cada petición clínica valida el token con Supabase Auth y lee el rol del perfil correspondiente al ID verificado. Sólo admin/admin_psicologia en Psicología y admin/admin_dentista en Dentista. No se aceptan roles de headers, cuerpo o user_metadata. Se rechazan sesiones anónimas. Cada responsable ve los registros de su área sujetos a RLS; no hay un modelo de asignación individual a profesionales aprobado.

El seguimiento está implementado pero desactivado por defecto mediante CLINICAL_ENABLE_UPDATES=false. Las tablas auditadas no tienen políticas UPDATE válidas. No se habilitó con credenciales privilegiadas. PATCH con cero filas devuelve 409, sin éxito falso.

Los nuevos roles son tipos admitidos por el código, no cuentas aprovisionadas. El alta real utiliza el servicio administrativo Auth ya existente del proyecto; debe verificarse en desarrollo que el trigger de perfiles persista el rol antes de dar acceso. No se incorporó una clave privada a esta rama. No se probó creando usuarios productivos.

El backend nuevo no remedia el acceso directo que las políticas públicas auditadas puedan permitir. perfiles debe protegerse contra elevación de rol por la Data API. Aunque se añadió el guard a Gestión de Usuarios, otros backends antiguos conservan reglas propias; no se declara aislamiento global ni certificación productiva. Ver PROPUESTA_SEGURIDAD_RLS.md.

## Verificación

Comandos desde la raíz:

```powershell
.\.venv-local\Scripts\python.exe -B -m unittest discover -s tests_clinical -p 'test_*.py' -v
node --test tests_clinical/test_frontend.cjs
git diff --check
```

Resultados: 16 pruebas Python y 6 pruebas Node pasan. Las pruebas bloquean la red y utilizan mocks/fakes con datos sintéticos.

Cobertura Python: matriz de roles y acceso cruzado de áreas; identidad inválida/anónima; headers falsificados; ausencia de alta clínica web y eliminación; filtros, UUID, fechas, paginación, detalle e historial; seguimiento bloqueado/habilitado con fake; preservación de paciente/profesional; validación de JSON/costos/sesiones/textos; errores y timeouts del adaptador; rechazo de claves privilegiadas; UPDATE sin filas; integración real de run.py con los once blueprints; rutas existentes de salud, login y archivos; login de los cinco tipos con proveedor falso; Gestión de Usuarios denegada a responsables de área y admisión de roles nuevos sin intentar aprovisionar cuentas cuando falta el proveedor.

Cobertura Node: serialización, centavos, zona horaria, PATCH parcial sin pérdida de precisión, omisión de cambios vacíos, estructura de vistas/enlaces y matriz de sidebar de cinco tipos. No es un test exhaustivo del negocio de los nueve módulos previos.

Pruebas de navegador interno con servidor sintético en loopback: carga y consulta de ambos módulos; búsqueda/historial; selección de expediente; navegación específica de Admin Psicología y Admin Dentista; actualización de nota psicológica y tratamiento/costo dental; recarga del detalle verificando persistencia sólo en memoria y conservación de fecha; ausencia de botón de alta. El primer borrador probó creación en fake antes de corregir el alcance, pero esas rutas de creación ya no forman parte del producto web.

Se consultó el dashboard publicado con la sesión administrativa proporcionada para confirmar la navegación existente. No se abrieron expedientes reales ni se accionaron controles de modificación en Render.

## MCP y auditoría

Se comprobó `codex mcp get supabase_formadig_readonly`: proyecto fijado a ctiqbycbkcftwuqgzxjb, read_only=true, grupos database/docs, herramientas list_tables/execute_sql/search_docs. OAuth estaba confirmado previamente. El servidor personalizado no aparece como herramienta invocable en esta sesión y no se dispone de una operación para recargar sus herramientas desde el chat. La llamada real disponible a list_tables del conector Supabase devolvió error de permisos. No se ampliaron permisos ni se usaron credenciales productivas para evitar el bloqueo.

La implementación se basó exclusivamente en los metadatos auditados, siguiendo la alternativa autorizada por el usuario. No se afirmó que el conector o el servidor personalizado hayan superado una consulta de esquema en esta fase.

## Estado de entrega

Implementado y probado con sustitutos: consulta/seguimiento de ambas áreas, tipos de acceso, navegación, login común, contratos y errores. Preparado para diseño visual sin reescribir servicios.

Pendiente: aprobar y ensayar RLS de lectura/seguimiento y perfiles en desarrollo, validar el contrato de solicitudes móviles, aprovisionar cuentas sintéticas con roles persistidos, probar el join y JWT reales de desarrollo, revisar concurrencia/auditoría/retención, revisar permisos de backends antiguos y ejecutar regresión de negocio completa. El esquema de Dentista no ofrece estatus de solicitud; cualquier ampliación requiere acuerdo y migración posterior.

No se certifica operación clínica productiva ni se publicó la rama. No se realizaron commits, push, PR, despliegues, cambios de Render ni lecturas/escrituras de registros clínicos reales.
