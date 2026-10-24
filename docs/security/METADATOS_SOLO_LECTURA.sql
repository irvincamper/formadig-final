-- SOLO METADATOS. No ejecuta DDL ni consulta filas de las tablas de aplicación.
SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity, c.relacl
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relname IN ('perfiles','modulo_psicologia','modulo_dental');
SELECT schemaname,tablename,policyname,roles,cmd,qual,with_check
FROM pg_policies
WHERE (schemaname='public' AND tablename IN ('perfiles','modulo_psicologia','modulo_dental'))
   OR policyname='RLS Traslados';
SELECT a.attrelid::regclass, a.attname, a.attacl
FROM pg_attribute a
WHERE a.attrelid IN ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
  AND a.attnum>0 AND NOT a.attisdropped;
SELECT t.tgrelid::regclass,pg_get_triggerdef(t.oid),pg_get_functiondef(p.oid),p.prosecdef,p.proacl,p.proconfig
FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid
WHERE NOT t.tgisinternal AND t.tgrelid IN ('auth.users'::regclass,'public.perfiles'::regclass,
    'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass);
SELECT conrelid::regclass,conname,pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid IN ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
   OR confrelid IN ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass);
SELECT pg_describe_object(d.classid,d.objid,d.objsubid) AS object,
       pg_describe_object(d.refclassid,d.refobjid,d.refobjsubid) AS dependency,d.deptype
FROM pg_depend d
WHERE d.refclassid='pg_class'::regclass AND d.refobjid IN
    ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass);
SELECT p.oid::regprocedure,p.prosecdef,p.proacl,p.proconfig
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname='public' AND (p.prosrc ILIKE '%perfiles%' OR p.prosrc ILIKE '%modulo_psicologia%' OR p.prosrc ILIKE '%modulo_dental%');
SELECT r.rolname,r.rolinherit,r.rolbypassrls,parent.rolname AS member_of
FROM pg_roles r LEFT JOIN pg_auth_members m ON m.member=r.oid
LEFT JOIN pg_roles parent ON parent.oid=m.roleid
WHERE r.rolname IN ('anon','authenticated');
