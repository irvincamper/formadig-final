-- Contención mínima: no concede acceso ni modifica expedientes o perfiles.
BEGIN;
SET LOCAL lock_timeout = '5s';
DO $$ BEGIN
    -- Si el corte seguro ya está instalado, no volver a cerrar módulos.
    IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public'
        AND tablename='modulo_psicologia' AND policyname='web_psychology_read') THEN
        IF (SELECT count(*) FROM pg_policies WHERE schemaname='public'
            AND tablename IN ('modulo_psicologia','modulo_dental')) <> 2
            OR (SELECT count(*) FROM pg_policies WHERE schemaname='public'
            AND tablename IN ('modulo_psicologia','modulo_dental')
            AND policyname IN ('web_psychology_read','web_dental_read')
            AND cmd='SELECT' AND roles=ARRAY['authenticated']::name[]
            AND qual LIKE '%web_role()%'
            AND qual LIKE '%atendido_por%auth.uid()%') <> 2
            OR EXISTS (SELECT 1 FROM pg_class WHERE oid IN
                ('public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
                AND (NOT relrowsecurity OR has_table_privilege('anon',oid,'SELECT')
                    OR has_table_privilege('authenticated',oid,'INSERT,UPDATE,DELETE,TRUNCATE'))) THEN
            RAISE EXCEPTION 'Corte presente pero distinto: revisar sin sobrescribir';
        END IF;
        RAISE NOTICE 'Corte coordinado presente; revisar su evidencia, sin modificarlo';
        RETURN;
    END IF;
    IF (SELECT count(*) FROM pg_policies WHERE schemaname='public'
        AND tablename IN ('modulo_psicologia','modulo_dental')) <> 4 THEN
        RAISE EXCEPTION 'Inventario clinico distinto: revisar antes de contener';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid IN
        ('public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
        AND attnum>0 AND NOT attisdropped AND attacl IS NOT NULL) THEN
        RAISE EXCEPTION 'Revisar privilegios clinicos de columna';
    END IF;
    ALTER TABLE public.modulo_psicologia ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.modulo_dental ENABLE ROW LEVEL SECURITY;
    REVOKE ALL ON public.modulo_psicologia, public.modulo_dental FROM PUBLIC, anon, authenticated;
    CREATE POLICY clinical_containment ON public.modulo_psicologia AS RESTRICTIVE
        FOR ALL TO PUBLIC USING (false) WITH CHECK (false);
    CREATE POLICY clinical_containment ON public.modulo_dental AS RESTRICTIVE
        FOR ALL TO PUBLIC USING (false) WITH CHECK (false);
END $$;
COMMIT;
