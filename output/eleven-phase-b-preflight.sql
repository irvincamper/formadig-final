-- PROPUESTA REVISABLE. Aplicar sólo tras aprovisionamiento autorizado y prueba aislada.
-- Exige aceptación explícita por conexión; no confundir con autorización para producción.
BEGIN READ ONLY;
SET LOCAL formadig.security_cutover='approved';
DO $$ BEGIN
    IF current_setting('formadig.security_cutover', true) IS DISTINCT FROM 'approved' THEN
        RAISE EXCEPTION 'Falta aprobar corte coordinado y comprobar compatibilidad';
    END IF;
END $$;
-- Abortamos ante nuevas políticas que pudieran combinarse mediante OR con las propuestas.
DO $$ BEGIN
    IF (SELECT count(*) FROM pg_policies WHERE schemaname='public'
        AND tablename IN ('perfiles','modulo_psicologia','modulo_dental')) NOT IN (7,9) THEN
        RAISE EXCEPTION 'Inventario de politicas cambio; revisar antes de cortar';
    END IF;
    IF (SELECT count(*) FROM pg_policies WHERE schemaname='public'
        AND tablename IN ('perfiles','modulo_psicologia','modulo_dental')) = 9
        AND (SELECT count(*) FROM pg_policies WHERE schemaname='public'
        AND tablename IN ('modulo_psicologia','modulo_dental')
        AND policyname='clinical_containment' AND permissive='RESTRICTIVE'
        AND cmd='ALL' AND qual='false' AND with_check='false') <> 2 THEN
        RAISE EXCEPTION 'Las politicas adicionales no son la contencion revisada';
    END IF;
END $$;
-- No cortar con cuentas web conocidas sin aprovisionamiento revisado.
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM formadig_private.web_roles WHERE role='admin') OR EXISTS (
        SELECT 1 FROM public.perfiles p LEFT JOIN formadig_private.web_roles r ON r.user_id=p.id
        WHERE p.rol IN ('admin','admin_traslados','admin_desayunos','psicologo','dentista')
          AND r.role IS DISTINCT FROM p.rol
    ) THEN
        RAISE EXCEPTION 'Completar revision y aprovisionamiento autorizado de cuentas antes del corte';
    END IF;
END $$;
-- Los nombres y tablas corresponden al SELECT de metadatos del 23-10-2026.
-- No se modifica el contenido ni los roles de ninguna cuenta existente.

SELECT true AS account_and_policy_preflights_passed, EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid IN ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass) AND attnum>0 AND NOT attisdropped AND attacl IS NOT NULL) AS unexpected_column_acl;
ROLLBACK;
