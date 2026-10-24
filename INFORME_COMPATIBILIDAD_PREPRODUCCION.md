# FORMADIG — Compatibilidad de preproducción (alcance web)

23 de octubre de 2026. Rama fix/autenticacion-seguridad; base conservada fcc5837. Este informe incorpora la aclaración del titular: **aplicación móvil completamente fuera del alcance**, sin buscar más código ni suponer identificadores. No hay staging Supabase identificado y autorizado.

## 1. Compatibilidad comprobada

Se verificaron mediante mocks los cinco roles web admin, admin_traslados, admin_desayunos, psicologo y dentista. La autorización sigue exigiendo identidad Auth verificada y correspondencia entre app_metadata.role, UUID y perfiles.rol. El laboratorio PostgreSQL verifica además el registro privado de roles y sus políticas.

No se acredita compatibilidad móvil ni se crean roles móviles. La carpeta MOVIL estaba vacía al inicio; tras la aclaración se retiraron los contratos y fixtures móviles propuestos. Sólo se conserva una regresión de datos históricos no web: actualizar metadatos Auth sin un rol web administrado no borra ni promueve su rol. No se modificó ninguna cuenta existente.

## 2. Endpoints afectados

- /api/auth/login y /api/auth/me: cinco roles canónicos, sin confiar en user_metadata ni perfiles por sí solos.
- /api/admin_usuarios: alta preparada mediante Auth Admin, seguida de lectura Auth y comprobación de perfil por UUID. Perfil faltante/discrepante devuelve 409 de conciliación, sin borrar la identidad ni fabricar otro perfil.
- /api/traslados: creación administrativa vincula al actor verificado; PATCH conserva registrado_por del solicitante y deja de preasignar registros al administrador. El cliente REST lleva JWT ordinario, timeout y no sigue redirecciones.
- /api/sms/webhook: permanece bloqueado por defecto. El receptor preparado exige firma Twilio, cuenta autorizada, URL externa configurada y una cola restringida. No se habilitó en run.py, Render ni producción.
- SMS automático de Transporte: se retiró la llamada al puerto antiguo localhost:5009 sin autenticación. La integración preparada usa la API unificada con JWT del personal; sigue desactivada por defecto y devuelve sms_status explícito.

Comidas, Mi Perfil y Chatbot conservan las protecciones de la fase anterior. No se cambió HTML/CSS ni main.

## 3. Problemas corregidos localmente

El trigger preparado ahora distingue cuentas con registro de rol administrado de perfiles históricos. Conserva roles históricos sin interpretarlos como privilegios; una retirada explícita del rol de una cuenta previamente administrada sí retira su autorización. Las pruebas cubren preservación y ausencia de promoción automática.

Transporte ya no necesita apropiarse del registro para actualizarlo. Se eliminó el mensaje que sugería desactivar RLS ante una actualización sin efecto; ahora devuelve una denegación/409 sin dar por aplicada la operación.

El alta profesional ya no considera suficiente que Auth devuelva un UUID: consulta nuevamente Auth y comprueba el perfil vinculado con el JWT del administrador. Un éxito 201 sigue indicando access_validation_pending: es un estado informativo, no una prohibición Auth. La aceptación operativa requiere la prueba real de acceso posterior.

## 4. Funciones pendientes o restringidas

- Altas reales, cambios de rol y bajas requieren autorización y procedimientos coordinados. Las bajas siguen bloqueadas para evitar cascadas.
- Psicología/Dentista permanecen sin escritura clínica real; consulta de información real pendiente de RLS aprobado.
- El webhook exige una cola persistente todavía no implementada para producción: deduplicación atómica por AccountSid/MessageSid, retención limitada y vínculo inequívoco con un mensaje saliente y un único traslado pendiente. Debe rechazar teléfonos ambiguos, eventos antiguos y solicitudes sin vínculo autorizado. La firma sola no concede permiso para actualizar filas.
- No se envió SMS ni se consultó Gemini. Los permisos reales de sms_logs, Transporte, Comidas y consumidores fuera del alcance no se certifican mediante mocks.

## 5. Migraciones

Las dos migraciones permanecen locales. La fase A prepara catálogo privado y trigger de aprovisionamiento confiable, sin convertir roles históricos. La fase B exige revisión/aprovisionamiento de cuentas web, revoca políticas públicas auditadas y conserva consulta propia de perfiles y edición no sensible, con consulta clínica por área. No se aplicaron en DIF.

No se añade dependencia de una aplicación móvil ausente a las pruebas locales de los cinco roles. Esto no equivale a aprobar cambios futuros sobre una base compartida: antes de aplicarlos, el titular debe autorizar el delta y evaluar su impacto sobre los consumidores existentes sin modificar sus roles implícitamente.

## 6. Pruebas

- 47 pruebas Python aprobadas (incluyen altas verificadas, solicitudes administrativas, firmas SMS y cuentas demo).
- 12 pruebas Node aprobadas.
- 92 controles PostgreSQL aislados aprobados; Auth/JWT simulados. No son pruebas Supabase Auth/PostgREST reales.
- Tres cuentas de demostración con login por formulario y permisos verificados en Chrome. Resultados en output/demo-users-browser.json.
- Sin cambios HTML/CSS; git diff --check correcto.

En los ensayos iniciales fallaron dos fixtures: un Mock no implementaba el context manager y una solicitud administrativa omitía campos obligatorios. Se corrigieron los fixtures, conservando las validaciones y aserciones de permisos. El CLI Playwright no permite fs/import en su VM; la prueba privada final utilizó la dependencia Playwright ya instalada con Chrome, sin trazas, capturas ni contraseñas en salida.

## 7. Requisitos para Auth y PostgREST reales

No se identificó entorno disponible/autorizado: el conector sólo enumera un proyecto personal INACTIVE distinto de DIF. No se activó ni se utilizó; no se crearon servicios cloud. Esto no demuestra que no existan otros proyectos fuera de la cuenta conectada.

Cuando se autorice staging: identificar referencia/propietario y confirmar por escrito que no es ctiqbycbkcftwuqgzxjb; preparar esquema compatible sin copiar datos reales; guardar claves fuera de Git; configurar Auth y PostgREST; ensayar las dos migraciones contra ese esquema con un operador autorizado; crear cuentas ficticias por Auth Admin en buzones controlados; comprobar correspondencia Auth/perfiles/registro; ejecutar positivos y negativos con JWT reales por Flask y REST; probar sesiones con roles antiguos y permisos de columna; mantener escrituras clínicas desactivadas. No basta un /health 200.

Las identidades del laboratorio SQL son tablas stub de una instancia nueva en TEMP: no son usuarios creados en Supabase Auth ni instrucciones para insertar directamente en auth.users real.

## 8. Riesgos de publicación

DIF conserva antecedentes confirmados de perfiles sin RLS, políticas clínicas públicas y trigger que toma rol editable. La consulta remota actual de cuentas de ensayo fue denegada. No se declaró corregida producción ni se crearon cuentas privilegiadas allí.

Faltan cuentas autorizadas, permisos reales verificados, conciliación de perfiles y prueba de regresión real. El registro privado propuesto requiere migración y aprovisionamiento controlado; agregar un nombre a perfiles no autoriza una cuenta.

## 9. Criterios pendientes para desplegar

Aprobar el SQL y el procedimiento de cuentas, preparar respaldo/reversión exacta, disponer de pruebas Auth/PostgREST reales en entorno autorizado, verificar la matriz de cinco roles y los consumidores compartidos, coordinar backend compatible con el corte de permisos y autorizar publicación. No se hizo push, merge, cambios en Render ni escrituras productivas.

El estado de las tres cuentas solicitadas y las instrucciones locales están en INFORME_USUARIOS_PRUEBA.md. El procedimiento futuro está en docs/security/ACTIVAR_CUENTAS_PROFESIONALES.md.
