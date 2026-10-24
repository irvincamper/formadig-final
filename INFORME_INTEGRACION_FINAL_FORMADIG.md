# Integración final FORMADIG

Fecha local: 23 de octubre de 2026. Estado: integración local preparada; corte productivo y publicación detenidos por las condiciones de recuperación y compatibilidad pendientes.

## 1. Las once identidades

Se conservan las once cuentas aprovisionadas: tres admin, cuatro admin_traslados, dos admin_desayunos, un psicologo y un dentista. La comprobación previa de Auth, perfiles y registro protegido resultó consistente. En esta intervención no se crearon identidades, no se cambiaron roles ni contraseñas. Las ocho cuentas históricas mantienen sus credenciales; no se dispone de sus contraseñas para probar sus sesiones individualmente. Las tres nuevas cuentas aprobaron nuevamente login real con el backend integrado. Credenciales e inventario nominal permanecen fuera del repositorio.

## 2. Migraciones realmente aplicadas

Estado remoto comprobado mediante CLI en DIF, ctiqbycbkcftwuqgzxjb:

| Archivo | Estado |
| --- | --- |
| 20261023202836_formadig_roles_protegidos.sql | Fase A aplicada previamente |
| 20261023202914_formadig_rls_corte_coordinado.sql | Fase B pendiente |
| 20261023214516_formadig_clinical_containment.sql | Contención aplicada previamente y registrada |
| 20261024012430_formadig_rls_modulos_legacy.sql | Nueva migración generada con CLI; probada localmente; no aplicada |

El nombre de la nueva migración usa fecha UTC. No se ejecutó db push ni se modificó el esquema productivo durante este cierre. La contención clínica permanece activa; las escrituras clínicas siguen deshabilitadas en el backend.

## 3. Seguridad corregida en código y SQL preparado

La autorización web conserva identidad verificada mediante Supabase Auth, JWT del usuario y rol administrado contrastado con perfiles y registro protegido. No se conceden privilegios desde user_metadata ni desde el rol enviado por el navegador.

La migración adicional protege traslados, desayunos_frios, desayunos_calientes, desayunos_eaeyd, sms_logs y la dependencia notificaciones. Activa RLS, reduce grants, separa áreas, impide cambiar propietario o identificador y elimina DELETE/TRUNCATE para los clientes. Los solicitantes autenticados sin rol web administrado conservan únicamente operaciones sobre sus propias solicitudes; no pueden aprobarlas. Los profesionales clínicos no obtienen esa excepción por figurar como propietarios. SMS queda limitado al remitente autorizado.

Se comprobaron los cuatro triggers de notificación y su función invocadora. Las notificaciones solo pueden consultarse y marcarse como leídas por su destinatario; el INSERT se reserva al flujo de trigger administrativo probado. Se fija search_path y se revoca ejecución pública de la función de notificación. La función log_traslado_change referencia historial_traslados ausente, pero no está conectada a un trigger; no se alteró ni se ejecutó.

Los preflight detienen el corte si cambian políticas, grants de columna, vistas dependientes, triggers o la correspondencia de las once identidades. Esto requiere repetir el inventario remoto inmediatamente antes del futuro corte.

## 4. Pruebas RLS con filas

scripts/verify_legacy_rls_isolated.py crea un clúster PostgreSQL 16 temporal aislado, utiliza exclusivamente datos sintéticos y ejecuta 274 comprobaciones. Incluye las 96 comprobaciones originales y las nuevas matrices de filas, acceso entre áreas, propietarios, JWT obsoletos, usuarios anónimos, INSERT/UPDATE no autorizados, cambios de estatus, SMS y notificaciones.

Se ejecuta la secuencia A, B y migración legacy. También se comprueba que la recuperación restrictiva sea repetible, conserve el contenido de las nueve tablas y deniegue acceso a anon/authenticated. El clúster se detiene al finalizar. Esto no certifica las políticas pendientes en Supabase real ni constituye restauración de una copia completa.

Un HTTP 200 con limit=0 no demuestra acceso a registros. Los riesgos remotos se apoyan en metadatos de RLS/grants; la eficacia propuesta se comprueba con filas ficticias en el laboratorio.

## 5. Compatibilidad de los módulos anteriores

Se confirmaron nombres de tablas, UUID, registrado_por, estatus y las operaciones del backend. Los tres módulos de alimentos ahora realizan un único PATCH a la tabla comprobada, con JWT validado, timeout y sin una escritura previa de usuario_admin. Se corrigieron los contratos url_comprobante_salud → url_salud y url_ine_tutor → url_ine. Una prueba reproduce las tres variantes y verifica que no se haga una consulta o escritura adicional.

La aplicación móvil no fue modificada. El contrato genérico de propietario autenticado fue probado con filas sintéticas; no se conocen ni inventan identificadores de sus roles. Sin su código o una petición autorizada representativa no se puede certificar el flujo móvil compartido. Esa validación continúa siendo una condición del corte.

## 6. Frontend integrado

Se creó codex/integracion-final-formadig desde origin/main 405ea508bfd9db69b47f9813d89d1a7fe2f83316. Se integró primero fix/autenticacion-seguridad y después origin/feat/frontend-general 5bf320100af50a88b32567ee6064e53cef8dcacd.

Se conservó el rediseño general. En core/formadig-core.js se combinaron los cambios de presentación con la verificación de identidad, revalidación del rol, menú y logout remoto; además se escapan los textos del encabezado. Se corrigió inputFecha no declarado en Traslados y se ajustó exclusivamente el comportamiento estrecho de formularios en modules.css para evitar desbordamiento horizontal. El indicador estático «RLS Activo» se sustituyó por «Acceso por rol» para no afirmar un estado de seguridad remoto todavía pendiente.

## 7. Git y conflictos

El único conflicto de la integración del frontend fue core/formadig-core.js y se resolvió combinando ambos contratos. Los merges locales son 26c5776 y 4ec5500. El cierre posterior se conserva mediante commit local en la misma rama; su SHA se consulta con git log -1. No se movió main ni se hizo push. Los archivos modificados e ignorados del checkout original se preservaron utilizando un worktree separado.

## 8. Resultados automatizados

| Verificación | Resultado | Alcance |
| --- | --- | --- |
| Python unittest | 49 aprobadas | Mocks y contratos backend |
| Node | 13 aprobadas | Autenticación y contratos frontend |
| PostgreSQL aislado | 274 comprobaciones | RLS con filas sintéticas y recuperación restrictiva |
| Playwright integrado | 23 combinaciones aprobadas | Cinco roles, navegación, formularios, perfil y responsive; Auth/datos simulados |
| Playwright con Supabase Auth real | Tres cuentas aprobadas | Login, identidad, dashboard, menú, rechazo de rol falsificado, logout y token inválido |

Evidencia: output/final-python.txt, final-node.txt, final-legacy-rls.json, final-integrated-ui.json y final-real-browser.json. scripts/verify_integrated_ui.cjs intercepta Auth y datos y cierra WebSockets: no demuestra persistencia real. Las capturas corresponden al diseño integrado; los módulos con datos se comprueban mediante fixtures.

Se preservaron los primeros resultados fallidos: servidor todavía no disponible, un error JavaScript y desbordamiento responsive. Las últimas ejecuciones se realizaron después de corregir esas causas, sin relajar las aserciones de ancho. No se consultaron expedientes para probar permisos ni se realizaron escrituras clínicas reales.

## 9. Estado de DIF y recuperación

En producción permanece el riesgo confirmado: perfiles y tablas legacy auditadas tienen RLS desactivado y privilegios amplios para clientes. La nueva corrección todavía no reduce ese riesgo remoto. Las tablas clínicas mantienen su contención restrictiva.

El intento de supabase db dump --linked --schema public,formadig_private falló por Docker no disponible. El archivo producido tiene cero bytes y NO es un respaldo utilizable. El log se conserva en el directorio privado local. No se afirma que exista un respaldo completo ni una restauración completa validada.

supabase/recovery/formadig_fail_closed.sql se probó en aislamiento: conserva datos y bloquea el acceso API a las nueve tablas afectadas. Es recuperación de contención y mantenimiento, no restauración del servicio ni sustituto de respaldo de esquema, permisos, funciones y datos autorizados.

## 10. GitHub y Render

No hubo publicación de esta integración ni modificaciones de Render. No existe un nuevo SHA desplegado verificado. La comprobación local de /health solo demuestra disponibilidad del proceso local; no certifica seguridad o despliegue. La instancia de revisión integrada utiliza http://127.0.0.1:8055/ mientras el proceso local permanezca activo.

## 11. Secuencia segura pendiente

1. Obtener un respaldo recuperable del delta autorizado, comprobar su integridad y ensayar su restauración fuera de producción. Resolver el requisito técnico del dump o disponer de una alternativa equivalente comprobada.
2. Verificar nuevamente metadatos remotos, historial de migraciones y correspondencia de las once identidades, sin cambiar contraseñas. Validar el contrato compartido de solicitudes con una petición móvil autorizada o documentación verificable.
3. Revisar visualmente la integración y preparar el backend con escrituras clínicas deshabilitadas. Mantener una ventana de mantenimiento para no exponer una aplicación incompatible entre cortes.
4. Ejecutar únicamente B y legacy revisadas, en ese orden probado. Ambas contienen BEGIN/COMMIT y gates de sesión distintos (formadig.security_cutover y formadig.legacy_cutover): usar una conexión controlada y valores de sesión comprobados, no una variable SET LOCAL que expire antes del siguiente archivo. No envolver sin revisión estos archivos en una transacción exterior. Mantener el servicio restringido entre las dos transacciones, verificar cada fase y registrar el historial oficial exclusivamente después del éxito. No repetir A ni contención ni usar push indiscriminado.
5. Si falla una comprobación, detener la apertura y aplicar únicamente el procedimiento restrictivo revisado; conservar datos e identidades. La restauración funcional deberá usar el respaldo previamente ensayado.
6. Verificar políticas y grants reales con JWT de los cinco roles y registros ficticios expresamente controlados. Confirmar denegaciones directas y operaciones administrativas por área; no usar service_role para superar RLS. Mantener clínica sin escrituras hasta probar sus controles específicos.
7. Solo cuando todas las condiciones estén satisfechas, integrar en main sin force push, desplegar backend compatible en Render y comprobar SHA, sesión, navegación y permisos. No basta /health.

## 12. Pendientes y recomendación

Listo localmente: integración frontend/backend, correcciones de contratos, migración legacy, procedimiento de contención y pruebas reproducibles. Las tres cuentas profesionales/de prueba ya existen; no requieren recreación ni nuevas contraseñas.

Pendiente: respaldo restaurable validado, compatibilidad compartida móvil, aplicación controlada de B y legacy, comprobación real posterior de RLS y aprobación visual de la integración. Hasta resolver estas condiciones no es seguro publicar ni habilitar los módulos clínicos reales. Este informe no declara resuelta la seguridad productiva de Supabase.
