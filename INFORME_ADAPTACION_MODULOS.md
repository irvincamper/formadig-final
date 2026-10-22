# FORMADIG — adaptación local de Psicología y Dentista

Validación posterior: el 22 de octubre de 2026 sí se ejecutaron pruebas reales de navegador sobre la demo sintética. Consultar INFORME_VALIDACION_VISUAL.md para resultados, capturas y la corrección del estado de paginación al fallar el listado. La ausencia de validación visual indicada en el contenido histórico de este informe ya no representa el estado actual. Esto no cambia los pendientes de persistencia/RLS real.

## Revalidación del 22 de octubre de 2026

El adjunto reenviado coincide con el alcance ya implementado. Se confirmó de nuevo la rama feat/psicologia-dentista y se conservaron todos los cambios pendientes, sin duplicar módulos ni introducir otra arquitectura. Se volvieron a ejecutar las 18 pruebas Python y las 6 Node: todas aprobaron; git diff --check no reportó errores. Se verificaron los ocho archivos de los dos módulos y las comprobaciones de roles/claims y capacidades en el código actual. Esta revalidación no consultó ni modificó Supabase ni Render. No se hicieron nuevas modificaciones funcionales por no existir diferencias de alcance; sólo se añadió esta evidencia al informe. Los límites de mocks, RLS pendiente y ausencia de prueba visual/persistencia real continúan vigentes.

21 de octubre de 2026. Rama `feat/psicologia-dentista`, base c74e6f7. Este documento y CONTRATO_FRONTEND.md describen el alcance vigente del último adjunto. Las auditorías anteriores son antecedentes, no resultados de esta fase.

## Resultado y reutilización

Se conservaron los avances de la rama; no se introdujo otro framework, login ni una arquitectura paralela. Se mantuvo el paquete clinical ya existente para compartir validación/autorización entre los dos adaptadores Flask. Cada módulo mantiene su estructura y arranque independientes.

| Referencia inspeccionada | Patrón reutilizado/adaptado |
|---|---|
| admin_traslados | Blueprint registrado en run.py, rutas colección/detalle, formulario y tabla lado a lado, selección y seguimiento |
| admin_desayunos_frios | Formulario asociado al registro seleccionado, búsqueda al escribir y paginación; se conserva paginación clínica de 25 ya implementada en la rama |
| admin_desayunos_calientes | Organización logica/vistas/diseno, endpoints GET y PATCH, manejo del estado del expediente |
| admin_espacios_eaeyd | Consulta, selección, llenado del formulario y confirmación de edición |
| admin_usuarios | Modal/formulario, selector de roles, listado y errores; ampliación local de perfiles profesionales |
| core/formadig-core.js y CSS existentes | Header, sidebar, sesión y estilo general; sin duplicarlos |

No se copiaron encabezados X-User-Role como autorización ni clientes privilegiados para el acceso clínico. Tampoco se replicó la carga completa de hasta 1000 expedientes de otros módulos: los servicios clínicos conservan filtros y paginación en el servidor. No se alteraron los backends de Traslados o Comidas.

## Estructura conservada

Dentro de Formadig/1_Sistema_DIF_Acatlan/modulos:

```text
admin_psicologia/
  logica/admin_psicologia_backend.py
  logica/admin_psicologia.js
  vistas/admin_psicologia.html
  diseno/admin_psicologia.css
admin_dentista/
  logica/admin_dentista_backend.py
  logica/admin_dentista.js
  vistas/admin_dentista.html
  diseno/admin_dentista.css
```

Los nombres admin_psicologia/admin_dentista se conservan para rutas y archivos; **no son los roles vigentes**. Los nuevos roles son exactamente `psicologo` y `dentista`.

## Archivos modificados en esta adaptación

- clinical/api.py: roles canónicos, coincidencia de claim confiable/perfil, alta exclusivamente sintética, atendido_por desde identidad verificada.
- core/clinical-ui.js: registro sintético sujeto a capacidades, POST o PATCH según selección, búsqueda con debounce de 250 ms y conservación del seguimiento parcial.
- Las dos vistas clínicas: textos sin dependencia móvil, formulario de registro/seguimiento, filtros de rango temporal y botón sintético bloqueado por defecto.
- core/formadig-core.js y dashboard.html: accesos para roles nuevos, rutas de módulos conservadas y sin cambios de permisos de Transporte/Comida.
- admin_usuarios/logica/admin_usuarios_backend.py: cinco roles web admitidos; administrador con identidad/claim/perfil consistentes; cliente PostgREST por petición con su JWT; alta por Auth Admin con app_metadata.role; cambio de rol a otro valor bloqueado hasta poder coordinar Auth/perfil.
- admin_usuarios/logica/admin_usuarios.js y vistas/admin_usuarios.html: etiquetas Psicólogo/Dentista y valores canónicos en el selector/listado.
- tests_clinical/fakes.py, test_api.py, test_frontend.cjs y serve_synthetic.py: identidades confiables sintéticas, negativas, alta mockeada y opciones de demostración.
- DATOS_PRUEBA_CLINICOS.sql: roles canónicos en las dependencias previstas; conserva todos sus guards. No se ejecutó.
- CONTRATO_FRONTEND.md, este informe y notas de fase en informes anteriores. .git/info/exclude ignora cachés no versionadas; las cachés rastreadas generadas por las pruebas se restituyeron a su estado previo.

Los adaptadores, estilos y registros de blueprints en run.py ya existían en los avances conservados; no se reescribieron. No se añadieron dependencias Python/npm.

## Funcionalidad y tablas

Ambas áreas disponen de listado, búsqueda textual, filtro por paciente, intervalo desde/hasta, detalle, historial por paciente y paginación. Psicología añade filtros tipo_atencion/estatus_caso. El formulario se llena con el registro seleccionado; la edición sólo se habilita según capacidades del backend.

Se verificaron nuevamente mediante el MCP **supabase_formadig_readonly**, ahora accesible, las 17 columnas de las tablas reales: nueve en modulo_psicologia y ocho en modulo_dental. Sólo se consultaron catálogos, sin expedientes ni modificaciones. La documentación oficial también respondió mediante search_docs. Se consultó el changelog oficial: la advertencia reciente de cifrados TLS afecta clientes antiguos; no se deshabilitó verificación TLS ni se cambiaron clientes para eludirla.

Psicología usa exclusivamente id, paciente_id, atendido_por, tipo_atencion, motivo_consulta, diagnostico_inicial, numero_sesion, estatus_caso, fecha_sesion. Dental usa id, paciente_id, atendido_por, motivo_consulta, diagnostico, tratamiento_realizado, costo_recuperacion, fecha_atencion.

Se conservan UUID, fechas ISO con zona/UTC, precisión decimal (numeric 10,2), límites de texto y sesión entera positiva. paciente_id/atendido_por referencian perfiles; perfiles depende de Auth. No se inventan pacientes/profesionales para la base real. En altas sintéticas atendido_por no se acepta del formulario; se asigna desde la identidad. En PATCH no se permite reasignar paciente, profesional ni ID.

Rutas existentes /api/psicologia y /api/dentista: GET colección, GET /capacidades, GET /{id}, GET /pacientes/{id}/historial, PATCH /{id} y POST colección bloqueado salvo modo sintético explícito. Sin DELETE clínico ni tablas nuevas.

## Usuarios y seguridad

Login único y Supabase Auth conservados. Se muestran los profesionales en Gestión de Usuarios. Crear una cuenta exige un administrador verificado y el servicio Auth Admin configurado únicamente en backend; si falta devuelve 503, sin perfiles huérfanos. Auth Admin sólo se utiliza para el alta de cuentas, no para consultar/escribir expedientes ignorando RLS.

La autorización clínica exige Auth.get_user válido, usuario no anónimo, perfil del mismo UUID y coincidencia app_metadata.role == perfiles.rol. Admin accede a ambas áreas; psicologo sólo Psicología; dentista sólo Dental. Un perfil manipulado por las políticas abiertas no basta para adquirir permisos. Claims ausentes/discordantes deniegan el acceso, aunque la interfaz muestre enlaces. Las cuentas previas sin claims confiables requieren aprovisionamiento administrativo revisado, no fallback a user_metadata.

Gestión de Usuarios usa el JWT del solicitante por petición para sus operaciones de tabla; no el cliente anónimo global. Actualizar campos conservando el mismo rol está implementado; cambiar a otro rol devuelve 409 antes de escribir para evitar divergencia entre Auth y perfil. La operación coordinada pendiente no se simula como realizada. Las reglas y rutas de los módulos anteriores se conservaron; esto no significa que sus riesgos históricos estén corregidos.

## Pruebas ejecutadas

- Python unittest: **18 pruebas aprobadas**, con red bloqueada y datos sintéticos. Cubren las dos áreas, 11 blueprints registrados, endpoints, filtros, UUID/fechas/costos/sesiones, historial, paginación, edición simulada, alta sólo en modo sintético explícito, identidad del profesional inmutable, negativas por área y claims discordantes.
- El mismo conjunto prueba login mockeado con cinco roles web, denegación de Gestión de Usuarios a profesionales, altas Auth Admin mockeadas con app_metadata correcto, 503 sin proveedor y edición administrativa por cliente JWT sin cambio parcial de rol.
- Node: **6 pruebas aprobadas**: serialización, precisión temporal/decimal, PATCH parcial, contrato HTML/enlaces y sidebar por rol.
- git diff --check: sin errores. Parser del fixture se conserva como validación sintáctica, no ejecución SQL.

Los avisos timeout/verify de la dependencia Supabase instalada son deprecaciones; no se cambiaron dependencias ni se ocultaron fallos. El ERROR RuntimeError del ensayo negativo comprueba saneamiento de errores, no una caída de Supabase real.

Estos resultados son unitarios/de integración local con mocks. No se ejecutó una prueba visual completa de navegador ni persistencia real contra Supabase. Los módulos antiguos se comprobaron a nivel de registro/rutas/recursos estáticos y login mockeado; no se declara una regresión funcional completa de sus flujos reales.

## Ejecución local sintética

Desde la raíz, PowerShell:

```powershell
& ./.venv-local/Scripts/python.exe -B -m tests_clinical.serve_synthetic --enable-creation --enable-updates
```

Abrir http://127.0.0.1:8011/demo, seleccionar Admin/Psicólogo/Dentista y entrar al módulo. Paciente ficticio: 00000000-0000-0000-0000-000000000002. Para alta, Registro sintético local limpia el formulario; para seguimiento, Ver detalle carga la atención. Los cambios existen sólo en memoria y desaparecen al detener el proceso. Ningún token demo es válido en Supabase. El servidor no quedó arrancado al entregar esta fase.

Repetir pruebas sin regenerar cachés rastreadas:

```powershell
& ./.venv-local/Scripts/python.exe -B -m unittest discover -s tests_clinical -p 'test_*.py'
node --test tests_clinical/test_frontend.cjs
```

Para el servidor real: configurar SUPABASE_URL y SUPABASE_KEY pública en el entorno del proceso y ejecutar `.venv-local/Scripts/python.exe -B run.py`. Conservar CLINICAL_ENABLE_UPDATES=false. No añadir CLINICAL_REPOSITORY_FACTORY en ese servidor. No usar el entorno .venv rastreado que apunta a otro equipo.

## Pendientes y frontend

No se alteró RLS remoto ni se crearon usuarios/filas reales, no se tocó Render/main ni se hicieron commits/push/despliegues. UPDATE real continúa bloqueado; DELETE no existe; las altas clínicas sólo se ejercitan en mocks por no disponer de controles de escritura aprobados. Las políticas permisivas existentes no son una autorización suficiente para habilitarlas.

Pendientes: RLS seguro, aprovisionamiento de claims de cuentas existentes y nuevos profesionales reales, sincronización administrativa de cambios de rol, verificación de FK/RLS con JWT ordinarios y persistencia real. DATOS_PRUEBA_CLINICOS.sql actualizado sigue sin ejecutar y requiere todas sus dependencias/validaciones.

Para el desarrollador frontend: conservar IDs/names y endpoints documentados en CONTRATO_FRONTEND.md, capacidad create/update decidida por servidor, scripts externos, data via textContent, accesibilidad y serialización UTC/decimal. Puede mejorar CSS y composición en diseno/ sin tocar seguridad ni añadir campos/operaciones. No convertir la demo en integración productiva ni habilitar controles sólo por localStorage.
