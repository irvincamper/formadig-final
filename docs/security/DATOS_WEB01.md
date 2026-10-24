# Datos ficticios WEB01

Los scripts están preparados y probados en PostgreSQL 17 aislado sobre una restauración del DDL real de DIF. No se ejecutaron en producción. No crean usuarios, perfiles ni roles y no habilitan escrituras clínicas mediante la aplicación.

Usar las tres cuentas nuevas autorizadas exclusivamente como identidades de prueba. Consultar sus UUID en el inventario privado; no versionarlos. La cuenta admin de prueba se usa como paciente ficticio técnico, sin vincular beneficiarios reales ni describir su salud. Los responsables clínicos son las cuentas nuevas de psicólogo y dentista. La UI muestra la identidad de esa cuenta de prueba; no se presenta como paciente real.

En SQL Editor, como administrador autorizado, ejecutar primero las cuatro líneas SET de la cabecera de `supabase/tests/web01_seed.sql`, sustituyendo los tres UUID. Ejecutar a continuación el archivo completo en la misma sesión. El gate `formadig.fixture_approved=web01` es obligatorio. No modificar variables de otras sesiones.

Se crean 30 filas por cada una de seis tablas: Traslados, Fríos, Calientes, EAEyD, Psicología y Dental. Los 180 UUID pertenecen exclusivamente al espacio `75000000-0000-0000-0001..0006-000000000001..000030`. Los nombres y motivos comienzan por `WEB01 FICTICIO`; no hay teléfonos de personas ni documentos/URLs reales. Las columnas obligatorias, defaults y FK se comprobaron en el esquema restaurado. Los alimentos referencian Auth y Traslados/perfiles y clínica conservan sus FK reales. No se desactivan triggers ni RLS.

La segunda inserción aborta por PK duplicada y revierte la transacción completa; no sobrescribe registros. Para repetir: limpieza controlada y luego seed. La limpieza utiliza simultáneamente UUID exactos, marcador y propietario; en clínica exige también profesional coincidente. Nunca borra Auth, perfiles, roles u otros UUID. Si alguien modifica marcador/propietario, la fila se conserva para revisión manual; no ampliar el DELETE para forzar su eliminación.

Tras B/legacy, comprobar listados con las cuentas correspondientes, búsqueda WEB01 y dos páginas clínicas (25+5). Para acceso directo usar `scripts/verify_web_cutover_real.py --after-cutover --base-url https://formadig-app.onrender.com`: sólo solicita `id` de esos UUID reservados y usa las tres contraseñas ya existentes del archivo privado. No se ha ejecutado aún porque las políticas remotas siguen pendientes.

No pulsar envío real de SMS durante las pruebas. Los cambios de estatus pueden generar notificaciones mediante el trigger existente. Para probarlos sin dejar efectos colaterales, utilizar una transacción SQL aislada con ROLLBACK; si se decide probarlos persistentemente por la UI, registrar primero los UUID exactos de las notificaciones generadas en un inventario privado. La limpieza suministrada no elimina notificaciones genéricas porque no tienen FK al registro original y no sería seguro identificarlas sólo por destinatario o texto.

La inserción clínica administrativa futura sirve exclusivamente para probar consultas autorizadas sobre datos ficticios. El API clínico continúa sin INSERT/UPDATE/DELETE. La migración B tampoco concede esas escrituras, incluso al administrador.
