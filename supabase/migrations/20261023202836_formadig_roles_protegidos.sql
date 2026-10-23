-- PROPUESTA REVISABLE. NO EJECUTADA EN PRODUCCION.
-- Fase A: no migra roles existentes ni los deduce de user_metadata/perfiles.
BEGIN;
CREATE SCHEMA formadig_private;
REVOKE ALL ON SCHEMA formadig_private FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA formadig_private TO authenticated;
CREATE TABLE formadig_private.web_roles (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('admin','admin_traslados','admin_desayunos','psicologo','dentista'))
);
ALTER TABLE formadig_private.web_roles ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON formadig_private.web_roles FROM PUBLIC, anon, authenticated;
GRANT SELECT ON formadig_private.web_roles TO authenticated;
CREATE POLICY own_role ON formadig_private.web_roles FOR SELECT TO authenticated
    USING (user_id = (SELECT auth.uid()));

-- SECURITY INVOKER: sólo lee el registro propio; no consulta perfiles ni recurre en RLS.
CREATE FUNCTION formadig_private.web_role() RETURNS text LANGUAGE sql STABLE
SECURITY INVOKER SET search_path = '' AS $$
    SELECT role FROM formadig_private.web_roles
    WHERE user_id = (SELECT auth.uid())
      AND role = (SELECT auth.jwt()->'app_metadata'->>'role')
      AND COALESCE((SELECT auth.jwt()->>'is_anonymous'), 'false') = 'false'
$$;
REVOKE ALL ON FUNCTION formadig_private.web_role() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION formadig_private.web_role() TO authenticated;

-- Sustituye el trigger existente, no añade un bypass general para consultas.
-- DEFINER es necesario exclusivamente para el aprovisionamiento Auth -> registro protegido.
-- Función privada, sin SQL dinámico, ruta fija, sin argumentos ni ejecución para clientes web.
CREATE FUNCTION formadig_private.sync_auth_web_role() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE canonical text;
BEGIN
    IF TG_TABLE_SCHEMA <> 'auth' OR TG_TABLE_NAME <> 'users' THEN
        RAISE EXCEPTION 'Trigger exclusivo de Auth';
    END IF;
    canonical := NEW.raw_app_meta_data->>'role';
    IF canonical NOT IN ('admin','admin_traslados','admin_desayunos','psicologo','dentista') THEN
        canonical := NULL;
    END IF;
    IF canonical IS NULL THEN
        DELETE FROM formadig_private.web_roles WHERE user_id = NEW.id;
    ELSE
        INSERT INTO formadig_private.web_roles(user_id,role) VALUES (NEW.id,canonical)
        ON CONFLICT(user_id) DO UPDATE SET role=EXCLUDED.role;
    END IF;
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.perfiles(id,nombre_usuario,nombre_completo,apellidos,rol,fecha_creacion)
        VALUES (NEW.id,NEW.raw_user_meta_data->>'nombre_usuario',
                NEW.raw_user_meta_data->>'nombre_completo',NEW.raw_user_meta_data->>'apellidos',canonical,now());
    ELSE
        -- Actualización explícita de app_metadata por administrador: no tocar otros datos.
        UPDATE public.perfiles SET rol=canonical WHERE id=NEW.id;
    END IF;
    RETURN NEW;
END
$$;
REVOKE ALL ON FUNCTION formadig_private.sync_auth_web_role() FROM PUBLIC, anon, authenticated;
-- Aborta si aparecen dependencias adicionales: sin CASCADE.
DROP TRIGGER on_auth_user_created ON auth.users;
DROP FUNCTION public.handle_new_user();
CREATE TRIGGER on_auth_user_created AFTER INSERT OR UPDATE OF raw_app_meta_data ON auth.users
FOR EACH ROW EXECUTE FUNCTION formadig_private.sync_auth_web_role();
COMMIT;
