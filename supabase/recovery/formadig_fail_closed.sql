-- Recuperación de acceso: mantenimiento cerrado, sin restaurar políticas públicas ni datos.
BEGIN;
SET LOCAL lock_timeout='5s';
DO $$ DECLARE t text; BEGIN
 FOR t IN SELECT unnest(ARRAY['perfiles','modulo_psicologia','modulo_dental','traslados',
  'desayunos_frios','desayunos_calientes','desayunos_eaeyd','sms_logs','notificaciones']) LOOP
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',t);
  EXECUTE format('REVOKE ALL ON public.%I FROM PUBLIC,anon,authenticated',t);
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename=t AND policyname='formadig_recovery_lockdown') THEN
   EXECUTE format('CREATE POLICY formadig_recovery_lockdown ON public.%I AS RESTRICTIVE FOR ALL TO PUBLIC USING(false) WITH CHECK(false)',t);
  END IF;
 END LOOP;
END $$;
COMMIT;
