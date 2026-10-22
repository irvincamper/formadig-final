# FORMADIG: matriz de integración académica

21 de octubre de 2026. Destino autorizado: DIF, ctiqbycbkcftwuqgzxjb. No incluye trabajo sobre la aplicación móvil. Inspección real realizada; pruebas funcionales y escrituras pendientes por incompatibilidad de protección de perfiles con consumidores desplegados. No equivalen a mocks.

## Resultados ejecutados ahora

| ID | Prueba real | Resultado y límite |
|---|---|---|
| A01 | Rama y Git | feat/psicologia-dentista; cambios conservados; sin commit/push/merge |
| A02 | MCP get_project | Denegado: You do not have permission to perform this action |
| A03 | Panel SQL del proyecto exacto | DIF y referencia confirmados; consultas nuevas de catálogos ejecutadas |
| A04 | Conteos clínicos | Psicología 0; Dental 0; sin leer expedientes |
| A05 | Dependencias sintéticas | 23 perfiles existentes; 0 perfiles con prefijo de prueba; 0 cuentas Auth reservadas |
| A06 | Catálogos de columnas y restricciones | Tipos, defaults, nullabilidad, PK/FK y dependencias refrescados; no se ejecutó el archivo completo inspect |
| A07 | Políticas y ACL | Lectura/inserción clínica pública, perfiles sin RLS, grants amplios; NO aprobado como seguridad correcta |
| A08 | Trigger Auth | Copia rol desde user_metadata; riesgo de autoasignación confirmado por definición, no explotado |
| A09 | Respaldo técnico local | JSON parseable: 3 tablas, 27 ACL de columna, 7 políticas, 11 restricciones y 1 trigger con función; procedimiento de reversión documentado |
| A10 | REST clínico directo sin JWT | Ambas tablas HTTP 200 con 0 filas; demuestra acceso actual al endpoint, no aislamiento correcto |
| A11 | HEAD Render /api/admin_usuarios/ sin sesión | ReadTimeout de 30 segundos; no pasó, no prueba funcional ni de autorización |
| A12 | Compatibilidad de consumidores | main y árbol local usan cliente público global para modificar perfiles; impedir escritura pública exige adaptación coordinada del backend |
| A13 | Parser local del fixture actualizado | 12 sentencias y 1 bloque PL/pgSQL; sólo sintaxis |

No se hicieron cambios remotos: no hay datos o políticas aplicados que revertir. CLINICAL_ENABLE_UPDATES permanece false.

## Condiciones para iniciar

1. DIF `ctiqbycbkcftwuqgzxjb` ya está autorizado como académico; no se exige otro proyecto. Resolver primero la compatibilidad del backend desplegado con la protección de perfiles, sin abrir permisos como atajo. Verificar siempre host/proyecto real.
2. Revisar el esquema y ejecutar DATOS_PRUEBA_CLINICOS.sql en modo inspect. Comparar tipos, PK, FK, restricciones, triggers, políticas, ACL de tabla y de columna con el informe auditado. Investigar cualquier diferencia; no adaptar el script silenciosamente.
3. Crear las cuentas ficticias del informe por Auth Admin API/panel en ese entorno; generar contraseñas únicas fuera del repositorio. Asignar app_metadata con marcador y rol confiables. No entregar claves administrativas al servidor clínico.
4. Aprobar y probar las políticas de lectura y protección de perfiles antes del acceso web. Aprobar UPDATE en una etapa posterior. El valor de CLINICAL_ENABLE_UPDATES debe seguir siendo false hasta ese momento.
5. Configurar sólo el proceso local de Flask con SUPABASE_URL de desarrollo, clave publishable de desarrollo y sin CLINICAL_REPOSITORY_FACTORY. No usar el servidor fake como prueba de Supabase.

## Identidades de prueba

| Alias de correo, sufijo @example.invalid | Perfil y app_metadata.role | Psicología | Dentista |
|---|---|---|---|
| fdg-clinical-admin | admin | Permitido | Permitido |
| fdg-clinical-psicologia | admin_psicologia | Permitido | Denegado |
| fdg-clinical-dentista | admin_dentista | Denegado | Permitido |
| fdg-clinical-traslados | admin_traslados | Denegado | Denegado |
| fdg-clinical-comidas | admin_desayunos | Denegado | Denegado |
| fdg-clinical-paciente-a | usuario_traslados | Denegado | Denegado |
| fdg-clinical-paciente-b | usuario_traslados | Denegado | Denegado |
| Sin sesión / Auth anónimo | Sin permiso clínico | Denegado | Denegado |

No basta cambiar localStorage: obtener una sesión real de Auth de desarrollo para cada cuenta. Probar un rol con perfil faltante o discordante con el claim confiable: no debe obtener datos clínicos.

## Matriz ejecutable por etapas

Las filas E siguientes están **PENDIENTES — no se aplicaron controles ni fixtures por el bloqueo de compatibilidad**. E01 tiene inspección independiente de metadatos completada (A06), pero el archivo inspect completo todavía no se ejecutó. No falta autorización para el destino académico.

| ID | Superficie y operación | Resultado que debe comprobarse | Evidencia mínima |
|---|---|---|---|
| E01 | SQL inspect en desarrollo | Tipos, nullabilidad, PK/FK/restricciones exactas; ninguna modificación | Salida de catálogos, referencia y fecha |
| E02 | SQL seed dos veces | 6 filas por tabla por defecto; mismos UUID, sin duplicación ni reinicio del seguimiento | Conteo sólo de UUID reservados antes/después |
| E03 | SQL seed con fixture_count=26 | 26 filas por tabla para paginación del frontend de 25 | Conteo de UUID reservados; entorno aislado |
| A01 | Login único con cada tipo | JWT real, rol del perfil correcto, áreas adecuadas en dashboard/sidebar | Capturas sintéticas y códigos HTTP sin tokens |
| A02 | Auth inexistente/vencido/anónimo | API Flask 401; nunca datos clínicos | Código y cuerpo saneado |
| A03 | Admin General, ambas áreas | GET listado/detalle/historial 200 con fixtures del área | UUID y conteo, sin secretos |
| A04 | Admin Psicología | Psicología 200; Dentista 403 en Flask | Dos solicitudes y cuerpos |
| A05 | Admin Dentista | Dentista 200; Psicología 403 en Flask | Dos solicitudes y cuerpos |
| A06 | Traslados/Comidas/pacientes | Ambas APIs clínicas 403 | Matriz de códigos por cuenta |
| A07 | Rol de header/localStorage/cuerpo falseado | No altera autorización del servidor | JWT de cuenta denegada, resultado denegado |
| R01 | REST directo con clave publishable, sin sesión | SELECT no revela filas; INSERT/PATCH/DELETE denegados | Estado y número de filas; verificar estado posterior |
| R02 | REST directo con JWT real por área | Mismo aislamiento que la matriz; rol contrario no recibe filas | HTTP + body; 200 con [] también es filtrado RLS, no acceso |
| R03 | Intentar PATCH perfiles.rol del propio usuario | Error de permisos y rol persistido sin cambios | Respuesta directa + lectura posterior del perfil propio |
| R04 | Intentar cambiar user_metadata.role mediante Auth | No cambia perfil/app_metadata ni acceso clínico | Lectura del perfil/claims propios y consulta clínica denegada |
| R05 | Intentar cambiar id, rol o nombre de otro perfil | Denegado; ninguna modificación | Lectura posterior de fixtures afectados |
| R06 | JWT válido de otro proyecto/perfil faltante | Auth/Flask deniega; ninguna fila | Códigos, sin guardar JWT |
| F01 | GET listado con q y filtros | Búsqueda por texto clínico; filtro UUID; tipo/estatus exacto sólo Psicología | IDs esperados/recibidos |
| F02 | Paginación API limit=2, offset=0/2 | Páginas sin solapamiento, orden fecha/UUID y has_more correcto | IDs de dos páginas |
| F03 | Paginación web con 26 fixtures por tabla | Primera página 25, segunda 1; volver conserva orden | Capturas y IDs extremos |
| F04 | Seleccionar expediente | Detalle coincide con fila; paciente/profesional correctos; nombre por join mínimo | Captura y comparación con consulta SQL del fixture |
| F05 | Historial paciente A/B | Sólo registros de ese paciente y de esa área | IDs esperados por paridad del índice |
| F06 | UUID, fechas, filtros inválidos | 400/404 controlados sin consultas amplias ni errores SQL expuestos | Casos negativos y respuestas |
| W00 | Flask con CLINICAL_ENABLE_UPDATES=false | PATCH 409 UPDATES_BLOCKED; sin cambio persistido | Antes/después de fixture |
| W01 | UPDATE RLS aún no aprobado | Ningún intento de habilitar bandera; registrar bloqueo | Configuración efectiva sin secretos |
| W02 | Tras aprobar UPDATE: REST directo con responsable correcto | PATCH del campo de seguimiento permitido y una sola fila devuelta | Respuesta y nueva consulta SQL/REST con otra petición |
| W03 | REST directo con rol contrario | UPDATE sin cambios; no confundir 200/[] con éxito | Comparación antes/después del UUID reservado |
| W04 | Cambiar paciente/profesional/id por REST | Denegado por privilegios de columna, sin reasignación | Lectura posterior |
| W05 | Habilitar bandera sólo en proceso dev tras aprobar W02–W04 | UI permite seguimiento; Flask PATCH 200 | Acta de aprobación + request saneado |
| W06 | Guardar nota psicológica/estatus/sesión | Cambian sólo campos enviados; fecha no editada conserva precisión | Nueva consulta PostgreSQL después de cerrar/reabrir detalle |
| W07 | Guardar tratamiento/costo dental 125.50 | Decimal y tratamiento persisten; paciente/profesional intactos | Nueva consulta PostgreSQL |
| W08 | Rechazar costo negativo, sesión cero, reasignación y DELETE | 400/405 o rechazo RLS; fixture sin cambios | Estado posterior y código |
| C01 | Login/dashboard/Traslados/Comidas/Usuarios con cuentas sintéticas | Navegación y contratos preservados; registrar cualquier incompatibilidad RLS heredada | Evidencias de desarrollo, sin datos reales |
| L01 | SQL clean dos veces | Sólo desaparecen UUID clínicos reservados; perfiles/Auth se conservan | Conteos antes/después, segunda ejecución sin error |
| L02 | SQL clean_profiles, sin otras referencias | Elimina sólo perfiles de cuentas marcadas; Auth queda explícitamente fuera | Conteo por IDs exactos |
| L03 | Dependencia ajena que referencia un fixture | Limpieza aborta y transacción revierte; no hay cascada colateral | Conteos previos y posteriores idénticos |

## Consultas y evidencia

Usar los UUID calculados por `md5('FORMADIG_CLINICAL_INTEGRATION_V1:psicologia:1')::uuid` y su equivalente `:dentista:1`, nunca un UUID obtenido de registros reales. El primer índice corresponde al paciente B, el segundo al A.

Para persistencia, abrir una nueva petición REST y una consulta PostgreSQL **filtrada por ese UUID de fixture** después del PATCH; no reutilizar el objeto JSON de respuesta ni la memoria del navegador como prueba. Comparar sólo columnas modificadas y columnas de identidad. Para probar RLS, usar JWT ordinarios y clave pública, no el operador SQL postgres ni service_role.

Conservar por caso: ID de matriz, hora, referencia dev, commit/base de código, actor sintético, superficie (Flask/REST/SQL/UI), resultado esperado, observado, estado PASS/FAIL/BLOCKED y ruta de evidencia local. No guardar contraseñas, claves, JWT, refresh tokens ni cookies en el informe o repositorio. Evidencias únicamente sintéticas.

No ejecutar suite general de scripts históricos `test_supabase*.py`: algunos realizan escrituras o registros en el proyecto productivo. Usar sólo la suite clínica delimitada y los casos reales aprobados de esta matriz.
