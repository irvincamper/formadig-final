# Metadatos confirmados el 23 de octubre de 2026

Proyecto ctiqbycbkcftwuqgzxjb. MCP execute_sql respondió sin permiso. Se consultó el SQL Editor autenticado con SELECT exclusivamente sobre pg_catalog/pg_policies; no se leyeron cuentas, perfiles ni expedientes. Las consultas y resúmenes de metadatos no contienen credenciales ni datos de pacientes. El editor quedó como borrador sin guardar; algunos reintentos de edición generaron errores sintácticos, sin efectos sobre datos/esquema.

- public.perfiles: RLS=false, force=false.
- public.modulo_psicologia y public.modulo_dental: RLS=true, force=false.
- Las tres tablas conceden a anon/authenticated/service_role SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER y MAINTAIN (ACL arwdDxtm observada). Las ACL particulares de columnas son NULL.
- Cada clínica tiene dos políticas PUBLIC permisivas: Lectura publica modulo_<area> FOR SELECT USING(true), e Insercion modulo_<area> FOR INSERT WITH CHECK(true). Para dental, el sufijo es modulo_dental; para Psicología, modulo_psicologia. No hay políticas UPDATE/DELETE clínicas.
- perfiles tiene Insercion automatica e Permitir insercion manual perfil (INSERT PUBLIC WITH CHECK(true)), y Lectura perfiles (SELECT PUBLIC USING(true)); actualmente RLS está desactivado.
- El trigger on_auth_user_created es AFTER INSERT ON auth.users y llama public.handle_new_user(). Inserta id,nombre_usuario,nombre_completo,apellidos,rol,fecha_creacion en perfiles. Obtiene rol de NEW.raw_user_meta_data->>'rol'. SECURITY DEFINER, propietario/ACL postgres, search_path no fijado. EXECUTE también concedido a PUBLIC, anon, authenticated, service_role. Una función de trigger no es por sí sola un RPC invocable normalmente: el riesgo confirmado de asignación ocurre por el alta Auth.
- La búsqueda de funciones públicas cuyo cuerpo menciona estas tablas encontró handle_new_user(). No certifica ausencia de SQL dinámico u otras superficies no inspeccionadas.
- anon y authenticated: sin BYPASSRLS, heredan, sin membresías adicionales observadas.
- FK de perfiles.id a auth.users.id ON DELETE CASCADE. Clínicas: paciente_id a perfiles con CASCADE; atendido_por a perfiles con SET NULL. Traslados y chatbot_historial también referencian perfiles. No se alteraron dependencias.
- pg_depend identifica la política RLS Traslados como consumidora de perfiles.id y perfiles.rol. Su condición exacta es `(SELECT perfiles.rol FROM perfiles WHERE perfiles.id=auth.uid())='admin_traslados' OR registrado_por=auth.uid()`, operación ALL, rol PUBLIC. La propuesta conserva lectura propia para evitar romper esa subconsulta. No amplía esa política para admin ni para otros roles.

La exposición efectiva por PostgREST, privilegios de esquema y otros endpoints/objetos no se acreditaron explotando acceso ni consultando registros. Los permisos y políticas observados justifican corregir la exposición; no se afirma haber extraído información clínica. No se alteraron RLS, funciones, privilegios ni Auth de producción.
