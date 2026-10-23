-- PROPUESTA REVISABLE. Aplicar sólo tras aprovisionamiento autorizado y prueba aislada.
-- Exige aceptación explícita por conexión; no confundir con autorización para producción.
BEGIN;
DO $$ BEGIN
    IF current_setting('formadig.security_cutover', true) IS DISTINCT FROM 'approved' THEN
        RAISE EXCEPTION 'Falta aprobar corte coordinado y comprobar compatibilidad';
    END IF;
END $$;
-- Abortamos ante nuevas políticas que pudieran combinarse mediante OR con las propuestas.
DO $$ BEGIN
    IF (SELECT count(*) FROM pg_policies WHERE schemaname='public'
        AND tablename IN ('perfiles','modulo_psicologia','modulo_dental')) <> 7 THEN
        RAISE EXCEPTION 'Inventario de politicas cambio; revisar antes de cortar';
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
ALTER TABLE public.perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.modulo_psicologia ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.modulo_dental ENABLE ROW LEVEL SECURITY;
DROP POLICY "Insercion automatica" ON public.perfiles;
DROP POLICY "Lectura perfiles" ON public.perfiles;
DROP POLICY "Permitir insercion manual perfil" ON public.perfiles;
DROP POLICY "Lectura publica modulo_psicologia" ON public.modulo_psicologia;
DROP POLICY "Insercion modulo_psicologia" ON public.modulo_psicologia;
DROP POLICY "Lectura publica modulo_dental" ON public.modulo_dental;
DROP POLICY "Insercion modulo_dental" ON public.modulo_dental;
REVOKE ALL ON public.perfiles, public.modulo_psicologia, public.modulo_dental FROM PUBLIC, anon, authenticated;
-- Las ACL de columnas auditadas eran NULL. Fallar al cambiar el inventario, no asumirlo.
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid IN
        ('public.perfiles'::regclass,'public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
        AND attnum>0 AND NOT attisdropped AND attacl IS NOT NULL) THEN
        RAISE EXCEPTION 'Revisar privilegios de columna antes de aplicar';
    END IF;
END $$;
GRANT SELECT ON public.perfiles, public.modulo_psicologia, public.modulo_dental TO authenticated;
GRANT UPDATE(nombre_usuario,nombre_completo,telefono,domicilio,apellidos,clave_elector,curp)
    ON public.perfiles TO authenticated;
-- No GRANT sobre rol/id, ni INSERT/DELETE/TRUNCATE; altas sólo por el trigger Auth.
CREATE POLICY web_profile_read ON public.perfiles FOR SELECT TO authenticated
USING (id=(SELECT auth.uid()) OR (SELECT formadig_private.web_role())='admin');
CREATE POLICY web_profile_update ON public.perfiles FOR UPDATE TO authenticated
USING ((SELECT formadig_private.web_role())='admin'
       OR (id=(SELECT auth.uid()) AND COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false'))
WITH CHECK ((SELECT formadig_private.web_role())='admin'
       OR (id=(SELECT auth.uid()) AND COALESCE((SELECT auth.jwt()->>'is_anonymous'),'false')='false'));
CREATE POLICY web_psychology_read ON public.modulo_psicologia FOR SELECT TO authenticated
USING ((SELECT formadig_private.web_role()) IN ('admin','psicologo'));
CREATE POLICY web_dental_read ON public.modulo_dental FOR SELECT TO authenticated
USING ((SELECT formadig_private.web_role()) IN ('admin','dentista'));
-- Fase de consulta: no se concede UPDATE clínico. Requiere autorización separada.
COMMIT;
