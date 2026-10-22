# FORMADIG: contrato web de Psicología y Dentista

Consolidado el 22 de octubre de 2026. Alcance vigente: adaptación local de módulos existentes, sin cambios remotos. Consulta, detalle, historial y filtros; registro y edición probados con repositorio sintético, también desde un navegador real (36 comprobaciones documentadas). En ejecución normal el registro está bloqueado y el seguimiento permanece desactivado. No existe eliminación clínica.

## Superficie exacta para el desarrollador frontend

Rutas relativas a la raíz del repositorio; no dependen de la carpeta del autor original.

| Archivo editable para apariencia | Cambios permitidos |
|---|---|
| Formadig/1_Sistema_DIF_Acatlan/modulos/admin_psicologia/vistas/admin_psicologia.html | Layout, contenedores, textos de ayuda, accesibilidad y presentación; conservar contratos de abajo |
| Formadig/1_Sistema_DIF_Acatlan/modulos/admin_psicologia/diseno/admin_psicologia.css | Estilos exclusivos de Psicología |
| Formadig/1_Sistema_DIF_Acatlan/modulos/admin_dentista/vistas/admin_dentista.html | Layout, contenedores, textos de ayuda, accesibilidad y presentación; conservar contratos de abajo |
| Formadig/1_Sistema_DIF_Acatlan/modulos/admin_dentista/diseno/admin_dentista.css | Estilos exclusivos de Dentista |
| Formadig/1_Sistema_DIF_Acatlan/css/clinical.css | Estilos compartidos de ambos módulos; revisar las dos vistas después de cualquier cambio |

Se pueden añadir imágenes/iconos propios no sensibles en diseno/assets/ de cada módulo y enlazarlos relativamente. Preferir los CSS específicos para no afectar otras pantallas. No introducir otro framework ni cambiar nombres de carpetas/rutas.

**Requieren revisión coordinada y no son superficie libre de diseño:** clinical/*.py, run.py, requirements.txt, core/clinical-ui.js, core/formadig-core.js, los JS de arranque de cada módulo, dashboard.html, login y Gestión de Usuarios, los CSS globales main.css/modules.css/dashboard.css, SQL/RLS y la configuración de permisos. El compañero puede proponer cambios, pero no alterar estos contratos para resolver una cuestión visual.

### Anclajes DOM y nombres que deben conservarse

- header.header; aside.sidebar con id sidebarMenu; main.workspace y su .workspace-content, usados por el encabezado y el menú existentes.
- Formularios attention-form y search-form. El botón submit de cada uno permanece dentro de su formulario; los demás botones conservan type=button.
- results sigue siendo tbody. Mantener status (role=status, aria-live), detail, history, previous, next, new-attention y los enlaces de retorno al dashboard. Los IDs son únicos. El render del detalle/listado sigue siendo responsabilidad del JS existente.
- Campos de search-form: q, paciente_id, desde, hasta; además tipo_atencion y estatus_caso en Psicología.
- Campos de attention-form Psicología: paciente_id, tipo_atencion, motivo_consulta, diagnostico_inicial, numero_sesion, estatus_caso, fecha_sesion.
- Campos de attention-form Dentista: paciente_id, motivo_consulta, diagnostico, tratamiento_realizado, costo_recuperacion, fecha_atencion.
- Conservar names, required, maxlength, type, min, max y step. No habilitar campos disabled desde CSS/JS; el servidor decide capacidades. No crear inputs editables para id, atendido_por ni rol.
- Conservar las cargas con defer de core/formadig-core.js, core/clinical-ui.js y logica/admin_<area>.js, en ese orden, y la llamada ClinicalUI.mount con psicologia/dentista. No duplicar eventos de guardar/buscar ni insertar scripts inline para eludir permisos.
- No cambiar endpoints, métodos HTTP, envoltorios data/pagination, códigos de error, tokens ni roles. Las rutas de módulo conservan admin_psicologia/admin_dentista; los roles son psicologo/dentista.
- Fechas locales en el formulario → ISO UTC; decimales como texto con dos posiciones al enviarlos; PATCH parcial preserva precisión histórica. No convertir edición en PUT ni en un POST de alta.
- No renderizar notas/listados mediante innerHTML. Conservar textContent para datos del usuario, mensajes de error accesibles y protección de doble envío existente.

### Criterio de aceptación de cambios visuales

Ejecutar las 18 pruebas Python y 6 Node indicadas en ENTREGA_TECNICA.md; iniciar únicamente la demo sintética para comprobar los tres roles. Repetir las 36 comprobaciones Playwright después de cambios relevantes de DOM y guardar nuevas capturas ficticias. Conservar la consulta de capacidades, los bloqueos reales y el estado de paginación durante carga/error. Entregar antes/después sin datos reales. No publicar demo, tokens ficticios como sesiones reales, archivos .env ni capturas de cuentas remotas.

## Accesos

Se mantiene el login único existente (`/api/auth/login`). Todos llegan al dashboard; no se necesitan formularios de login duplicados. La navegación usa el rol del login; el backend exige además identidad verificada y app_metadata.role confiable coincidente con perfiles.rol. Tipos soportados en la administración de usuarios:

| Rol | Área operativa |
|---|---|
| admin | Traslados, Comidas, Psicología y Dentista |
| admin_traslados | Traslados |
| admin_desayunos | Comidas (Fríos, Calientes, EAEyD) |
| psicologo | Psicología |
| dentista | Dentista |

Se conservan los enlaces de soporte y perfil existentes. Los responsables clínicos no obtienen acceso a Gestión de Usuarios. El sidebar y el dashboard ocultan las demás áreas operativas para ellos. La autorización de las APIs nuevas se realiza en el servidor; ocultar un enlace no es control de acceso. Los backends antiguos conservan sus reglas, salvo el guard de Gestión de Usuarios añadido para proteger las altas y cambios de rol.

Nombres de roles añadidos por petición explícita del usuario; no se crearon cuentas, contraseñas ni privilegios productivos. El alta real requiere un administrador autorizado, el servicio Auth administrativo ya existente, el perfil con el rol persistido y pruebas en desarrollo. Si ese servicio no está configurado, el alta devuelve 503 en lugar de aparentar éxito. No se añadió ninguna clave privada.

## Archivos y presentación

El frontend servido por run.py está en `Formadig/1_Sistema_DIF_Acatlan`. Cada módulo conserva `logica/`, `vistas/` y `diseno/`:

- `admin_psicologia/vistas/admin_psicologia.html`: consulta y seguimiento de Psicología.
- `admin_dentista/vistas/admin_dentista.html`: consulta y seguimiento dental.
- JavaScript específico: inicia `ClinicalUI.mount` en `core/clinical-ui.js`.
- Estilos: CSS existentes main/modules/dashboard, `css/clinical.css` y archivo específico por módulo.
- Servicios Flask: paquete `clinical/`, fuera de la raíz estática.

Las vistas siguen el encabezado y sidebar existentes. En escritorio, expediente/seguimiento a la izquierda y solicitudes a la derecha, como el módulo de Traslados proporcionado por el usuario; en pantallas pequeñas se apilan. No son un rediseño visual definitivo.

El diseñador puede modificar HTML y CSS manteniendo los nombres de campos y los IDs `attention-form`, `search-form`, `history`, `results`, `detail`, `status`, `previous`, `next` y `sidebarMenu`, además de `new-attention`. `results` es tbody. Conservar el botón submit dentro de attention-form, labels, aria-live del estado y scripts externos. El JS coloca datos mediante textContent, sin interpretarlos como HTML. No mover la autorización al navegador.

## Autenticación

Cada consulta o edición envía `Authorization: Bearer <access_token>` desde `localStorage.supabase_token`. El servidor consulta Supabase Auth `/auth/v1/user` y después `perfiles(id,rol)` filtrado por el ID verificado. Exige que app_metadata.role coincida con perfiles.rol. No usa user_metadata ni X-User-Role ni roles del cuerpo como prueba. Si faltan claims confiables, devuelve 403; no confiar en perfiles abiertos por RLS para autorizar.

La API Psicología acepta sólo `admin` y `psicologo`; Dentista sólo `admin` y `dentista`. Sesiones anónimas se rechazan. Los claims de paciente/profesional no dan permisos por sí solos. Actualmente cada responsable autorizado consulta todos los registros visibles de su área; no se ha definido una asignación individual de casos al profesional.

Supabase recibe clave pública SUPABASE_KEY y JWT del usuario en cada petición, sin sesión global compartida y sin service_role. Configuración faltante o clave privilegiada produce 503. Los nuevos endpoints no usan el cliente administrativo de Gestión de Usuarios.

## Endpoints

`{base}` representa `/api/psicologia` o `/api/dentista`.

| Método | Ruta | Resultado |
|---|---|---|
| GET | {base}/capacidades | read=true; create sólo en modo sintético explícito, delete=false, update según servidor |
| GET | {base}/ | Listado con filtros y paginación |
| GET | {base}/{id} | Detalle o 404 si no existe/no es visible |
| GET | {base}/pacientes/{paciente_id}/historial | Historial de ese paciente en el área |
| PATCH | {base}/{id} | Seguimiento parcial, bloqueado por defecto |
| POST | {base}/ | 405 por defecto. Sólo ensayo sintético explícito: valida, asigna atendido_por desde identidad y devuelve 201 |

No existe operación DELETE ni PUT. GET de colección admite con/sin slash final.

### Parámetros de consulta

- `q`: busca en los textos clínicos de esa tabla (motivo/diagnóstico y demás campos de texto), máximo 120 caracteres. Letras, números, espacios y guiones; rechaza operadores PostgREST. No es un buscador de nombres de pacientes.
- `paciente_id`: UUID exacto. Historial exige coincidencia con su ruta si se repite como filtro.
- `desde`, `hasta`: ISO 8601 con T y zona obligatoria, inclusive; años 1900–2100. Inicio no posterior al final.
- `tipo_atencion`, `estatus_caso`: sólo Psicología, igualdad exacta, máximo 120 caracteres.
- `limit`: entero 1–100, predeterminado 25; `offset`: entero 0–1000000, predeterminado 0.
- Parámetros repetidos/desconocidos producen 400.

Se filtra en Supabase, no después de descargar la tabla. Orden: fecha descendente (NULL al final) y UUID descendente. Se obtiene una fila adicional para has_more, sin total global. Se expande únicamente `paciente.nombre_completo` mediante la FK auditada; se muestra UUID si el nombre no es visible. No se descargan CURP, teléfonos ni domicilio para los listados nuevos.

Respuesta sintética de listado (campos abreviados):

```json
{"data":[{"id":"00000000-0000-0000-0000-000000000003","paciente_id":"00000000-0000-0000-0000-000000000002","paciente":{"nombre_completo":"Paciente sintético"},"motivo_consulta":"Seguimiento ficticio"}],"pagination":{"limit":25,"offset":0,"has_more":false}}
```

Detalle: `{"data":{...}}`, con todas las columnas explícitas de la tabla y expansión mínima del nombre. Las filas sintéticas del servidor de demostración no provienen de producción.

### Seguimiento

No se permite cambiar `id`, `paciente_id`, `atendido_por` ni rol de una atención existente. La web actualiza la atención seleccionada. El registro sólo se ejercita en la demo sintética; allí el backend asigna al profesional desde la identidad ficticia verificada. En registros existentes se conserva el profesional asignado, sin depender de una implementación móvil.

Psicología permite PATCH de `tipo_atencion`, `motivo_consulta`, `diagnostico_inicial`, `numero_sesion`, `estatus_caso`, `fecha_sesion`.

Dentista permite PATCH de `motivo_consulta`, `diagnostico`, `tratamiento_realizado`, `costo_recuperacion`, `fecha_atencion`. El esquema auditado no tiene estatus dental; no se inventó ni agregó una columna de aprobación/rechazo. Un flujo adicional requiere un contrato de datos aprobado, fuera de esta entrega visual.

Validaciones: motivo/tipo/estatus no vacíos cuando se envían; tipo/estatus hasta 120 caracteres, textos clínicos hasta 10000. Diagnósticos y tratamiento opcionales aceptan NULL o vacío (normalizado a NULL). Sesión debe ser entero 1–2147483647, sin booleanos. Costo de 0 a 99999999.99, máximo dos decimales, sin NaN/Infinity; se envía como string decimal para conservar centavos. Fechas ISO con zona y rango anterior, normalizadas a UTC. No se inventaron catálogos de tipo/estatus. JSON objeto no vacío, máximo 64 KiB; campos desconocidos se rechazan.

Las fechas del formulario se interpretan en la zona local del equipo. Si no se cambia la fecha mostrada, el PATCH la omite para preservar segundos y precisión histórica. Sólo se envían cambios, no un reemplazo completo del registro.

Ejemplo ficticio PATCH Psicología:

```json
{"diagnostico_inicial":"Nota de seguimiento sintética","numero_sesion":2,"estatus_caso":"En proceso"}
```

Ejemplo ficticio PATCH Dentista:

```json
{"tratamiento_realizado":"Procedimiento ficticio","costo_recuperacion":"125.50"}
```

Éxito: HTTP 200 `{"data":{...},"message":"Seguimiento actualizado."}`. Con `CLINICAL_ENABLE_UPDATES=false` (predeterminado) se devuelve 409 UPDATES_BLOCKED. La UI consulta capacidades y deja el detalle sin edición. Un UPDATE que devuelve cero filas produce 409 UPDATE_NOT_APPLIED, no éxito. Habilitar edición exige aprobación y ensayos RLS en desarrollo; nunca usar una clave privilegiada para eludirlos.

## Errores

Formato clínico: `{"error":"Mensaje seguro","code":"CODIGO","fields":{"campo":"Descripción"}}`. fields puede estar vacío.

401 sesión inválida/ausente; 403 rol o RLS denegado; 400 parámetros/campos inválidos; 404 registro no visible; 405 creación web no permitida; 409 edición bloqueada/no aplicada/conflicto; 413 cuerpo excesivo; 422 restricción de datos; 502 respuesta upstream inválida; 503 configuración/conectividad; 504 timeout; 500 error inesperado saneado.

No mostrar errores SQL internos ni registrar cuerpos clínicos/tokens. Respuestas con Cache-Control: no-store. Ante timeout de escritura consultar antes de reintentar: no hay idempotencia ni control optimista de concurrencia en esta fase. Si expira la sesión, iniciar sesión de nuevo; no se agregó refresh automático.

## Ejecución y demo

Aplicación local: `.\.venv-local\Scripts\python.exe run.py`, con variables Supabase públicas y sesión válida. No se realizaron escrituras productivas para probarla.

Demo sin red ni base de datos:

```powershell
.\.venv-local\Scripts\python.exe -B -m tests_clinical.serve_synthetic --enable-creation --enable-updates
```

Abrir `http://127.0.0.1:8011/demo`, elegir Admin General/Psicólogo/Dentista. Se usan tokens ficticios válidos sólo en el fake; no sirven en Supabase. Registros precargados y nuevas altas sólo en memoria. Sin --enable-updates se prueba seguimiento bloqueado; sin --enable-creation se prueba alta bloqueada. El servidor escucha sólo en loopback, no se importa desde run.py y no debe publicarse. Detenerlo pierde los datos sintéticos.

## Ensayo sintético vigente

Ejecutar `.venv-local/Scripts/python.exe -B -m tests_clinical.serve_synthetic --enable-creation --enable-updates` y abrir http://127.0.0.1:8011/demo. Seleccionar una de las tres identidades ficticias y entrar al área. El botón Registro sintético local limpia y habilita el formulario sólo cuando capacidades.create=true. La bandera no se habilita por variables de entorno: requiere CLINICAL_SYNTHETIC_MODE, CLINICAL_ENABLE_CREATION y un repositorio inyectado explícito. Nada se guarda en Supabase: los datos se pierden al cerrar el proceso. Los tokens de este servidor nunca son válidos contra el backend real.

El frontend puede cambiar composición y CSS sin alterar names/IDs, tipos numéricos, límites, serialización UTC, tratamiento textContent de datos ni capacidades. No presentar un botón habilitado como permiso concedido; la API siempre vuelve a comprobarlo. Administración permite crear profesionales vía Auth Admin configurado sólo en backend y con app_metadata confiable; si falta servicio responde 503. Edición de datos usa el JWT del administrador por petición; cambiar el rol a otro valor está bloqueado hasta disponer de actualización coordinada Auth/perfil. Los roles anteriores admin_psicologia/admin_dentista no se migran ni se aceptan silenciosamente; sólo se conservan esos nombres en rutas/archivos de módulo.
