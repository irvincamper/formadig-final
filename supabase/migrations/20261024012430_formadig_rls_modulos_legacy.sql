-- Corte explícito; probado primero con registros sintéticos. No aplicado por generar este archivo.
-- Depende de Fase A. Orden probado: A, B y este corte, con backend JWT compatible.
BEGIN;
SET LOCAL lock_timeout='5s';
DO $$ BEGIN
 IF current_setting('formadig.legacy_cutover',true) IS DISTINCT FROM 'approved' THEN
  RAISE EXCEPTION 'Falta revisar respaldo, backend y contratos compartidos';
 END IF;
 IF (SELECT count(*) FROM formadig_private.web_roles) <> 11 OR EXISTS (
  SELECT 1 FROM formadig_private.web_roles r LEFT JOIN auth.users u ON u.id=r.user_id
  LEFT JOIN public.perfiles p ON p.id=r.user_id
  WHERE r.role IS DISTINCT FROM p.rol OR r.role IS DISTINCT FROM u.raw_app_meta_data->>'role'
 ) THEN RAISE EXCEPTION 'Revisar las once identidades antes del corte'; END IF;
 IF (SELECT md5(string_agg(tablename||'|'||policyname||'|'||roles::text||'|'||cmd||'|'||coalesce(qual,'')||'|'||coalesce(with_check,''),E'\\n' ORDER BY tablename,policyname))
 FROM pg_policies WHERE schemaname='public' AND tablename IN
 ('traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','sms_logs','notificaciones'))
 IS DISTINCT FROM '8b2d058184e6f68f055d512419a78345'
 THEN RAISE EXCEPTION 'Definiciones legacy distintas del inventario revisado'; END IF;
 IF (SELECT count(*) FROM pg_policies WHERE schemaname='public' AND tablename IN
  ('traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','sms_logs','notificaciones')) <> 15
 THEN RAISE EXCEPTION 'Inventario de politicas legacy cambio'; END IF;
 IF EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid IN
  ('public.traslados'::regclass,'public.desayunos_frios'::regclass,'public.desayunos_calientes'::regclass,
   'public.desayunos_eaeyd'::regclass,'public.sms_logs'::regclass,'public.notificaciones'::regclass)
  AND attnum>0 AND NOT attisdropped AND attacl IS NOT NULL)
 THEN RAISE EXCEPTION 'Revisar grants de columna'; END IF;
 IF EXISTS (SELECT 1 FROM pg_depend d JOIN pg_rewrite r ON d.classid='pg_rewrite'::regclass AND r.oid=d.objid
  JOIN pg_class v ON v.oid=r.ev_class WHERE v.relkind IN ('v','m') AND d.refobjid IN
  ('public.traslados'::regclass,'public.desayunos_frios'::regclass,'public.desayunos_calientes'::regclass,
   'public.desayunos_eaeyd'::regclass,'public.sms_logs'::regclass,'public.notificaciones'::regclass))
 THEN RAISE EXCEPTION 'Auditar vistas dependientes antes del corte'; END IF;
 IF (SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgname IN
  ('trigger_notif_traslados','trigger_notif_frios','trigger_notif_calientes','trigger_notif_eaeyd')) <> 4
 OR (SELECT prosecdef FROM pg_proc WHERE oid='public.crear_notificacion_por_cambio_estatus()'::regprocedure)
 THEN RAISE EXCEPTION 'Revisar contrato de notificaciones'; END IF;
END $$;
CREATE FUNCTION formadig_private.can_use_legacy_area(area text, owner_id uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY INVOKER SET search_path='' AS $$
 SELECT COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false' AND (
  (SELECT formadig_private.web_role()) IN ('admin',area)
  OR (owner_id=(SELECT auth.uid()) AND NOT EXISTS
   (SELECT 1 FROM formadig_private.web_roles WHERE user_id=(SELECT auth.uid())))
 )
$$;
REVOKE ALL ON FUNCTION formadig_private.can_use_legacy_area(text,uuid) FROM PUBLIC,anon;
GRANT EXECUTE ON FUNCTION formadig_private.can_use_legacy_area(text,uuid) TO authenticated;
-- Conserva el propietario; un solicitante no puede adjudicarse un dictamen administrativo.
CREATE FUNCTION formadig_private.guard_support_mutation() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path='' AS $$
DECLARE area text;
BEGIN
 IF current_user NOT IN ('anon','authenticated') THEN RETURN NEW; END IF;
 area := CASE WHEN TG_TABLE_NAME='traslados' THEN 'admin_traslados' ELSE 'admin_desayunos' END;
 IF TG_OP='UPDATE' AND (NEW.id IS DISTINCT FROM OLD.id OR NEW.registrado_por IS DISTINCT FROM OLD.registrado_por)
 THEN RAISE EXCEPTION 'Propietario e identidad inmutables' USING ERRCODE='42501'; END IF;
 IF NOT COALESCE((SELECT formadig_private.web_role()) IN ('admin',area),false) THEN
  IF (TG_OP='INSERT' AND NEW.estatus IS DISTINCT FROM 'Pendiente')
   OR (TG_OP='UPDATE' AND NEW.estatus IS DISTINCT FROM OLD.estatus)
  THEN RAISE EXCEPTION 'permission denied: dictamen reservado al area administrativa' USING ERRCODE='42501'; END IF;
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION formadig_private.guard_support_mutation() FROM PUBLIC,anon,authenticated;
DO $$ DECLARE t text; pol record; cols text; seq text; area text;
BEGIN
 FOR t IN SELECT unnest(ARRAY['traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','sms_logs','notificaciones']) LOOP
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',t);
  EXECUTE format('REVOKE ALL ON public.%I FROM PUBLIC,anon,authenticated',t);
  FOR pol IN SELECT policyname FROM pg_policies WHERE schemaname='public' AND tablename=t LOOP
   EXECUTE format('DROP POLICY %I ON public.%I',pol.policyname,t);
  END LOOP;
  IF t IN ('traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd') THEN
   area := CASE WHEN t='traslados' THEN 'admin_traslados' ELSE 'admin_desayunos' END;
   EXECUTE format('GRANT SELECT,INSERT ON public.%I TO authenticated',t);
   SELECT string_agg(quote_ident(attname),',') INTO cols FROM pg_attribute
    WHERE attrelid=format('public.%I',t)::regclass AND attnum>0 AND NOT attisdropped
    AND attname NOT IN ('id','registrado_por','usuario_admin') AND attgenerated='';
   EXECUTE format('GRANT UPDATE(%s) ON public.%I TO authenticated',cols,t);
   EXECUTE format('CREATE POLICY area_rows ON public.%I FOR ALL TO authenticated USING
    (formadig_private.can_use_legacy_area(%L,registrado_por)) WITH CHECK
    (formadig_private.can_use_legacy_area(%L,registrado_por))',t,area,area);
   EXECUTE format('CREATE TRIGGER formadig_guard_support BEFORE INSERT OR UPDATE ON public.%I
    FOR EACH ROW EXECUTE FUNCTION formadig_private.guard_support_mutation()',t);
   EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON public.%I(registrado_por)','formadig_owner_'||t,t);
  END IF;
  seq := pg_get_serial_sequence(format('public.%I',t),'id');
  IF seq IS NOT NULL THEN
   EXECUTE format('REVOKE ALL ON SEQUENCE %s FROM PUBLIC,anon,authenticated',seq);
   IF t='sms_logs' THEN EXECUTE format('GRANT USAGE ON SEQUENCE %s TO authenticated',seq); END IF;
  END IF;
 END LOOP;
END $$;
GRANT SELECT,INSERT ON public.sms_logs TO authenticated;
CREATE POLICY sms_own_read ON public.sms_logs FOR SELECT TO authenticated USING
 ((SELECT formadig_private.web_role()) IN ('admin','admin_traslados','psicologo','dentista')
  AND enviado_por=(SELECT auth.uid())::text);
CREATE POLICY sms_own_insert ON public.sms_logs FOR INSERT TO authenticated WITH CHECK
 ((SELECT formadig_private.web_role()) IN ('admin','admin_traslados','psicologo','dentista')
  AND enviado_por=(SELECT auth.uid())::text);
GRANT SELECT,INSERT ON public.notificaciones TO authenticated;
GRANT UPDATE(leida) ON public.notificaciones TO authenticated;
CREATE POLICY notification_own_read ON public.notificaciones FOR SELECT TO authenticated USING
 (usuario_id=(SELECT auth.uid()) AND COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false');
CREATE POLICY notification_own_seen ON public.notificaciones FOR UPDATE TO authenticated
 USING (usuario_id=(SELECT auth.uid()) AND COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false')
 WITH CHECK (usuario_id=(SELECT auth.uid()) AND COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false');
-- Sólo el trigger de UPDATE auditado, no un INSERT REST arbitrario de notificaciones.
CREATE POLICY notification_from_support_trigger ON public.notificaciones FOR INSERT TO authenticated WITH CHECK
 (pg_trigger_depth()=1 AND (SELECT formadig_private.web_role()) IN ('admin','admin_traslados','admin_desayunos'));
ALTER FUNCTION public.crear_notificacion_por_cambio_estatus() SET search_path='';
REVOKE EXECUTE ON FUNCTION public.crear_notificacion_por_cambio_estatus() FROM PUBLIC,anon,authenticated;
CREATE INDEX IF NOT EXISTS formadig_notification_owner ON public.notificaciones(usuario_id);
CREATE INDEX IF NOT EXISTS formadig_sms_owner ON public.sms_logs(enviado_por);
COMMIT;
