-- SELECT exclusivamente: metadatos y conteos de identidades, nunca expedientes.
SELECT n.nspname AS schema,c.relname AS tabla,c.relrowsecurity AS rls,
 has_table_privilege('anon',c.oid,'SELECT') AS anon_select,
 has_table_privilege('authenticated',c.oid,'SELECT') AS authenticated_select,
 has_table_privilege('authenticated',c.oid,'INSERT') AS authenticated_insert,
 has_table_privilege('authenticated',c.oid,'DELETE') AS authenticated_delete,
 has_table_privilege('authenticated',c.oid,'TRUNCATE') AS authenticated_truncate
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relname IN
 ('perfiles','modulo_psicologia','modulo_dental','traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','sms_logs','notificaciones')
ORDER BY c.relname;
SELECT schemaname,tablename,policyname,permissive,roles,cmd,qual,with_check
FROM pg_policies WHERE schemaname IN ('public','formadig_private') ORDER BY tablename,policyname;
SELECT r.role,count(*) AS cuentas,
 count(*) FILTER(WHERE r.role IS DISTINCT FROM p.rol OR r.role IS DISTINCT FROM u.raw_app_meta_data->>'role') AS inconsistencias
FROM formadig_private.web_roles r LEFT JOIN public.perfiles p ON p.id=r.user_id
LEFT JOIN auth.users u ON u.id=r.user_id GROUP BY r.role ORDER BY r.role;
SELECT version FROM supabase_migrations.schema_migrations ORDER BY version;
