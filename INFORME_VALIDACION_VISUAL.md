# FORMADIG — validación visual y funcional de Psicología y Dentista

Fecha: 22 de octubre de 2026, America/Mexico_City. Rama comprobada: `feat/psicologia-dentista`.

**Resultado: 36 comprobaciones de navegador aprobadas, 0 fallidas en la pasada final. Frontend apto para entregar a otro desarrollador para mejorar su apariencia, dentro del alcance sintético probado.** No es una validación de Supabase real ni una autorización de publicación.

## Entorno y ejecución efectiva

- Servidor Flask existente `tests_clinical.serve_synthetic`, iniciado automáticamente en http://127.0.0.1:8011 con `--enable-creation --enable-updates`. Se reinició después de corregir los defectos para repetir sobre memoria limpia.
- Navegador automatizado real: Chromium 155.0.8059.85, mediante Playwright CLI. No se sustituyó la prueba visual por inspección del HTML.
- Viewports: 1440×1000 y 800×1000. Se revisaron capturas reales de ambos módulos, el formulario seleccionado/editado y el estado de error.
- Sesiones seleccionadas mediante los botones de la demo: admin, psicologo y dentista. Son identidades y tokens ficticios del repositorio en memoria, NO autenticaciones contra Supabase Auth.
- Primera semilla: una atención por módulo. En la pasada final se creó una atención de prueba y otras 24 por área mediante los botones/formularios: 26 registros por módulo, suficientes para probar la segunda página.
- Paciente sintético: UUID 00000000-0000-0000-0000-000000000002. Nombres, motivos y notas marcados como sintéticos. No se consultaron expedientes reales ni se modificaron registros remotos.

## Pruebas y resultados

Los resultados individuales están en [resultados-visuales.json](<output/playwright/resultados-visuales.json>) (29 comprobaciones) y [resultados-campos.json](<output/playwright/resultados-campos.json>) (7 adicionales).

| Flujo | Evidencia comprobada | Resultado |
|---|---|---|
| Psicólogo / Dentista | Cada profesional entra a su área; su sidebar no incluye el otro módulo ni Gestión de Usuarios | Aprobado, ambos |
| Acceso directo al área ajena | HTML puede cargar, pero capacidades devuelve 403; sin filas y formulario deshabilitado | Aprobado, ambos |
| Administrador general | Puede abrir ambos módulos y dispone de ambos enlaces | Aprobado |
| Listado | Semilla visible y actualización del listado después de crear | Aprobado, ambos |
| Búsqueda al escribir | Término inexistente produce cero filas; marcador recupera la atención concreta | Aprobado, ambos |
| Filtros e historial | Fecha futura excluye registros; tipo psicológico no coincidente excluye; UUID permite historial; sin UUID aparece error | Aprobado |
| Selección y detalle | Ver detalle carga el UUID correcto, los campos y el detalle; paciente queda no editable | Aprobado, ambos |
| Registro sintético | Botón Registro sintético local limpia/habilita formulario; guardar envía POST 201 y muestra el registro | Aprobado, ambos |
| Edición sintética | Guardar edición envía PATCH 200; recargar y seleccionar mediante un GET nuevo recupera el motivo editado | Aprobado, ambos |
| Sin cambios | Guardar sin modificar muestra No hay cambios para guardar | Aprobado, ambos |
| Campos obligatorios | Formulario vacío no válido y sin POST | Aprobado, ambos |
| UUID inválido | POST 400; error UUID visible y marcado en la interfaz | Aprobado, ambos |
| Números inválidos | Sesión -1/1.5 y costo -1/0.001 rechazados por validación nativa, sin POST | Aprobado |
| Fecha de filtro inválida | GET 400 con mensaje Fecha inválida visible | Aprobado, ambos |
| Precisión monetaria | 123.40 se conserva en la representación del registro | Aprobado |
| Paginación | Primera página de 25; Siguiente abre página 2 con registros; Anterior vuelve a página 1 | Aprobado, ambos |
| Navegación | Volver al Panel carga dashboard; tarjeta devuelve al módulo autorizado | Aprobado, ambos |
| Menú | Botón lateral pliega/despliega y modifica realmente su estado | Aprobado |
| Cierre de sesión | Borra sesión demo; al volver al módulo se pide iniciar sesión y no se habilita escritura | Aprobado |
| Error de listado | HTTP 503 provocado muestra error, vacía tabla, desactiva paginación y permite recuperar con búsqueda | Aprobado tras corrección, ambos |
| Viewport estrecho | Composición apilada conservada; controles presentes y capturas revisadas | Aprobado para 800 px; no certifica todos los dispositivos |
| JavaScript | Listener pageerror sin excepciones no capturadas durante el flujo principal | Aprobado |
| Favicon demo | Endpoint devuelve 204, sin 404 | Aprobado tras corrección |

La persistencia comprobada es **en memoria del proceso Flask, a través de una nueva consulta HTTP después de recargar el navegador**. No se comprobó ni se afirma persistencia PostgreSQL. Al apagar la demo se pierden estas atenciones, como corresponde al ensayo.

## Errores encontrados y corregidos

### 1. Paginación obsoleta después de un fallo HTTP

Fallo reproducido: listado con más de 25 filas → siguiente página habilitada → simular 503 al buscar → tabla vacía, pero Siguiente permanecía habilitado. Evidencia original en [fallo-paginacion-antes.json](<output/playwright/fallo-paginacion-antes.json>): rows=0, nextDisabled=false.

Corrección mínima en `core/clinical-ui.js`: deshabilitar ambos controles mientras se carga y, al fallar la petición vigente, vaciar filas, poner hasMore=false y mantener ambos botones deshabilitados. Se conserva el control de secuencia para no aplicar respuestas obsoletas. No se cambiaron estilos ni endpoints.

Repetición desde navegador: prueba del 503 y recuperación aprobada en Psicología y Dentista; paginación normal también aprobada.

### 2. Favicon inexistente en la demo

La primera visita generaba GET /favicon.ico → 404 en consola. Se añadió una respuesta 204 exclusivamente al servidor sintético. Se reinició y verificó mediante una petición del navegador. No se modificó el servidor real ni se creó un rediseño/icono.

### Observación visual descartada como defecto

Una captura larga realizada con scroll hacía aparecer el header sticky sobre el título. Se comprobó la página al inicio: cabecera y título no se solapan. Se repitieron capturas con scroll=0. No se alteró el CSS para corregir un artefacto de captura.

## Consola, HTTP y aislamiento

En la pasada principal se observaron seis respuestas de error previstas: dos 403 de acceso cruzado, dos 400 de UUID inválido y dos 503 inyectados por Playwright para probar recuperación. Las pruebas adicionales provocaron otros dos 400 por fecha inválida. No son fallos espontáneos del servidor ni resultados aprobados ocultando errores.

No hubo excepciones JavaScript no capturadas. La carga del dashboard/login intenta descargar Google Fonts del código existente; se bloqueó expresamente esa petición externa en el navegador de pruebas, por lo que aparecen mensajes de recurso ERR_FAILED y se utiliza la fuente de respaldo. Es una dependencia visual externa documentada, no una excepción JavaScript ni acceso a datos clínicos. No se cambió el estilo compartido para esconder ese diagnóstico.

La automatización permitió tráfico sólo al origen local y bloqueó otras salidas; las únicas solicitudes externas observadas fueron tres intentos a fonts.googleapis.com. No hubo solicitudes de navegador a Supabase o Render. El backend arrancado fue el sintético, que usa FakeRepository y nunca conecta la base.

## Evidencias visuales

Capturas finales con datos ficticios, después de la corrección:

### Psicología: selección y edición recuperada tras recargar

![Psicología sintética](<output/playwright/psicologia-editado.png>)

### Dentista: detalle, tratamiento y costo sintéticos

![Dentista sintético](<output/playwright/dentista-editado.png>)

Otras capturas en `output/playwright/`: psicologia-validacion.png, dentista-validacion.png, psicologia-error503.png, dentista-error503.png, psicologia-estrecho.png, dentista-estrecho.png, admin-psicologia.png y admin-dentista.png. Las capturas son evidencia del layout básico, no aprobación de un diseño definitivo. Los diagnósticos con etiquetas `<b>` son texto ficticio literal; no se interpretan como HTML en la vista.

## Regresión local y archivos

Se repitieron las 18 pruebas Python y las 6 Node existentes: todas aprobadas. git diff --check sin errores. El RuntimeError del ensayo unitario negativo y los avisos de deprecación de Supabase son diagnósticos conocidos de esas pruebas, no conexiones ni fallos de la demo real.

Archivos de esta fase: corrección en core/clinical-ui.js; favicon en tests_clinical/serve_synthetic.py; automatizaciones tests_clinical/visual_flow.js, visual_fields.js y visual_error_probe.js; resultados/capturas en output/playwright; este informe y nota de actualización en INFORME_ADAPTACION_MODULOS.md. Se ignoraron localmente los artefactos auxiliares .playwright-cli sin eliminar otros archivos del usuario.

Los tres scripts Playwright son funciones para `playwright-cli run-code --filename`, no suites @playwright/test. El probe de error reproduce el caso y describe el estado; en una nueva memoria vacía hay que crear primero más de 25 filas para que ese estado inicial sea significativo.

## Repetición

Desde la raíz, en terminales separadas:

```powershell
& ./.venv-local/Scripts/python.exe -B -m tests_clinical.serve_synthetic --enable-creation --enable-updates
npx --yes --package @playwright/cli playwright-cli -s=formadig-visual open http://127.0.0.1:8011/demo
npx --yes --package @playwright/cli playwright-cli -s=formadig-visual --raw run-code --filename tests_clinical/visual_flow.js
npx --yes --package @playwright/cli playwright-cli -s=formadig-visual --raw run-code --filename tests_clinical/visual_fields.js
```

Usar un proceso demo limpio para repetir exactamente los conteos; después cerrar sólo esa sesión del navegador y detener ese proceso Flask.

## Pendientes y entrega al frontend

Sí puede entregarse el frontend para trabajar su apariencia: los flujos locales solicitados ya se ejercitaron desde el navegador con clics, respuestas HTTP y comprobaciones del contenido, no sólo verificando la existencia de botones. Conservar IDs/names/endpoints y la autorización backend descritos en CONTRATO_FRONTEND.md. No se realizó un rediseño.

Siguen pendientes Supabase Auth real, RLS, altas/ediciones clínicas reales, persistencia PostgreSQL, regresión completa de módulos anteriores con servicios reales y verificación en otros navegadores/dispositivos. La identidad de la demo comparte un UUID profesional sintético y cambia su rol por el selector; no acredita aislamiento de múltiples profesionales reales ni asignación individual de casos.

Se conservaron las restricciones: Supabase/Render/RLS/main sin cambios; sin commits, push ni despliegues. CLINICAL_ENABLE_UPDATES real no fue habilitado. El servidor de demostración fue detenido y la sesión Playwright cerrada al terminar; se comprobó que no quedara un listener en el puerto 8011. No quedó un servicio de prueba funcionando.
