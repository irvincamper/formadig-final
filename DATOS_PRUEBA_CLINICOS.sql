-- FORMADIG: fixtures en desarrollo aislado o en DIF académico autorizado.
-- NO EJECUTADO. No crea cuentas Auth ni guarda contraseñas.
-- Primero: aprobar/verificar el destino, crear las 7 cuentas del informe mediante
-- Auth Admin API/panel, con app_metadata confiable. No insertar en auth.users a mano.
-- Después, en LA MISMA sesión SQL y en un destino aprobado:
--   SET formadig.environment = 'isolated-development';
--   SET formadig.project_ref = '<REF_REAL_DEL_PROYECTO_DE_DESARROLLO>';
--   SET formadig.development_approved = 'FORMADIG_CLINICAL_INTEGRATION_V1';
--   SET formadig.fixture_action = 'inspect'; -- inspect | seed | clean | clean_profiles
--   SET formadig.fixture_count = '6';        -- 2..26 por tabla; 26 prueba paginación web
-- Alternativa autorizada por el titular el 2026-10-21, exclusivamente DIF académico:
--   SET formadig.environment = 'academic-authorized';
--   SET formadig.project_ref = 'ctiqbycbkcftwuqgzxjb';
--   SET formadig.academic_approved = 'FORMADIG_CLINICAL_INTEGRATION_V1';
-- El resto de los controles y dependencias sigue siendo obligatorio.
-- Revisar el host/proyecto real por separado: los SET son un seguro operativo,
-- no una prueba criptográfica del destino. No aplican a una producción institucional.
-- inspect (predeterminado): sólo metadatos; seed preserva fixtures ya existentes;
-- clean: sólo UUID clínicos reservados; clean_profiles: además perfiles propios,
-- abortando si hay otras referencias. Las cuentas Auth se conservan explícitamente.

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

-- Preflight de metadatos: sin SELECT de expedientes/perfiles/usuarios.
SELECT table_name, column_name, udt_name, is_nullable, column_default,
       numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_schema='public' AND table_name IN ('modulo_psicologia','modulo_dental','perfiles')
ORDER BY table_name, ordinal_position;

SELECT conrelid::regclass AS tabla, conname, pg_get_constraintdef(oid,true) AS definicion
FROM pg_constraint
WHERE conrelid IN (to_regclass('public.modulo_psicologia'),to_regclass('public.modulo_dental'),to_regclass('public.perfiles'))
   OR confrelid IN (to_regclass('public.modulo_psicologia'),to_regclass('public.modulo_dental'));

SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class
WHERE oid IN (to_regclass('public.modulo_psicologia'),to_regclass('public.modulo_dental'),to_regclass('public.perfiles'));
SELECT schemaname,tablename,policyname,roles,cmd,qual,with_check FROM pg_policies
WHERE schemaname='public' AND tablename IN ('modulo_psicologia','modulo_dental','perfiles');
SELECT table_name,grantee,privilege_type FROM information_schema.table_privileges
WHERE table_schema='public' AND table_name IN ('modulo_psicologia','modulo_dental','perfiles');
SELECT table_name,column_name,grantee,privilege_type FROM information_schema.column_privileges
WHERE table_schema='public' AND table_name IN ('modulo_psicologia','modulo_dental','perfiles');
SELECT tgrelid::regclass AS tabla,tgname,pg_get_triggerdef(oid) AS definicion FROM pg_trigger
WHERE NOT tgisinternal AND tgrelid IN
 (to_regclass('public.modulo_psicologia'),to_regclass('public.modulo_dental'),to_regclass('public.perfiles'));

DO $fixtures$
DECLARE
  ns constant text := 'FORMADIG_CLINICAL_INTEGRATION_V1';
  academic_ref constant text := 'ctiqbycbkcftwuqgzxjb';
  academic_authorized boolean;
  target_ref text := current_setting('formadig.project_ref',true);
  action text := coalesce(nullif(current_setting('formadig.fixture_action',true),''),'inspect');
  fixture_count integer := coalesce(nullif(current_setting('formadig.fixture_count',true),''),'6')::integer;
  names text[] := ARRAY['admin','psicologia','dentista','traslados','comidas','paciente-a','paciente-b'];
  roles text[] := ARRAY['admin','psicologo','dentista','admin_traslados','admin_desayunos','usuario_traslados','usuario_traslados'];
  account_ids uuid[] := ARRAY[]::uuid[];
  psych_ids uuid[];
  dental_ids uuid[];
  expected record;
  actual record;
  account record;
  fk record;
  i integer;
  patient uuid;
  professional uuid;
  record_id uuid;
  module_name text;
  table_name text;
  found_external boolean;
  actual_type text;
BEGIN
  IF action NOT IN ('inspect','seed','clean','clean_profiles') THEN
    RAISE EXCEPTION 'Acción de fixture no permitida';
  END IF;
  IF fixture_count NOT BETWEEN 2 AND 26 THEN
    RAISE EXCEPTION 'fixture_count debe estar entre 2 y 26';
  END IF;

  -- No escribir si faltan tablas/columnas o cambian tipos del esquema auditado.
  FOR expected IN SELECT * FROM (VALUES
    ('modulo_psicologia','id','uuid'),('modulo_psicologia','paciente_id','uuid'),
    ('modulo_psicologia','atendido_por','uuid'),('modulo_psicologia','tipo_atencion','text'),
    ('modulo_psicologia','motivo_consulta','text'),('modulo_psicologia','diagnostico_inicial','text'),
    ('modulo_psicologia','numero_sesion','int4'),('modulo_psicologia','estatus_caso','text'),
    ('modulo_psicologia','fecha_sesion','timestamptz'),
    ('modulo_dental','id','uuid'),('modulo_dental','paciente_id','uuid'),
    ('modulo_dental','atendido_por','uuid'),('modulo_dental','motivo_consulta','text'),
    ('modulo_dental','diagnostico','text'),('modulo_dental','tratamiento_realizado','text'),
    ('modulo_dental','costo_recuperacion','numeric'),('modulo_dental','fecha_atencion','timestamptz'),
    ('perfiles','id','uuid'),('perfiles','rol','text'),('perfiles','nombre_usuario','text'),
    ('perfiles','nombre_completo','text'),('perfiles','fecha_creacion','timestamptz')
  ) AS x(tab,col,typ) LOOP
    SELECT c.udt_name INTO actual_type FROM information_schema.columns c
      WHERE c.table_schema='public' AND c.table_name=expected.tab AND c.column_name=expected.col;
    IF actual_type IS DISTINCT FROM expected.typ THEN
      RAISE EXCEPTION 'Esquema distinto del auditado: %.%', expected.tab, expected.col;
    END IF;
  END LOOP;
  IF (SELECT count(*) FROM information_schema.columns c WHERE c.table_schema='public' AND c.table_name='modulo_psicologia')<>9
     OR (SELECT count(*) FROM information_schema.columns c WHERE c.table_schema='public' AND c.table_name='modulo_dental')<>8 THEN
    RAISE EXCEPTION 'Número de columnas clínicas distinto del auditado';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_schema='public'
    AND c.table_name IN ('modulo_psicologia','modulo_dental')
    AND c.column_name IN ('id','paciente_id','motivo_consulta','tipo_atencion') AND c.is_nullable<>'NO') THEN
    RAISE EXCEPTION 'Nullabilidad obligatoria distinta del esquema auditado';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_schema='public' AND c.table_name='perfiles'
    AND c.is_nullable='NO' AND c.column_default IS NULL AND c.is_identity='NO' AND c.is_generated='NEVER'
    AND c.column_name NOT IN ('id','nombre_usuario','nombre_completo','rol','fecha_creacion')) THEN
    RAISE EXCEPTION 'Perfil requiere columnas adicionales: revisar antes de insertar';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_schema='public'
      AND c.table_name='modulo_dental' AND c.column_name='costo_recuperacion'
      AND c.numeric_precision=10 AND c.numeric_scale=2) THEN
    RAISE EXCEPTION 'Se esperaba costo_recuperacion numeric(10,2)';
  END IF;
  FOR module_name IN SELECT unnest(ARRAY['modulo_psicologia','modulo_dental','perfiles']) LOOP
    IF NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conrelid=to_regclass('public.'||module_name)
      AND c.contype='p' AND pg_get_constraintdef(c.oid,true)='PRIMARY KEY (id)') THEN
      RAISE EXCEPTION 'PK inesperada en %',module_name;
    END IF;
  END LOOP;
  FOR expected IN SELECT * FROM (VALUES
    ('modulo_psicologia','paciente_id','public.perfiles','c'),
    ('modulo_psicologia','atendido_por','public.perfiles','n'),
    ('modulo_dental','paciente_id','public.perfiles','c'),
    ('modulo_dental','atendido_por','public.perfiles','n'),
    ('perfiles','id','auth.users','c')
  ) AS x(tab,col,target,delete_action) LOOP
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint c
      JOIN pg_attribute source ON source.attrelid=c.conrelid AND source.attnum=c.conkey[1]
      JOIN pg_attribute dest ON dest.attrelid=c.confrelid AND dest.attnum=c.confkey[1]
      WHERE c.conrelid=to_regclass('public.'||expected.tab) AND c.contype='f'
        AND cardinality(c.conkey)=1 AND source.attname=expected.col
        AND c.confrelid=to_regclass(expected.target) AND dest.attname='id'
        AND c.conname=expected.tab||'_'||expected.col||'_fkey'
        AND c.confdeltype::text=expected.delete_action
    ) THEN RAISE EXCEPTION 'FK o borrado referencial distinto: %.%',expected.tab,expected.col;
    END IF;
  END LOOP;
  IF action='inspect' THEN
    RAISE NOTICE 'Sólo preflight de metadatos. Sin inserts, updates ni deletes.';
    RETURN;
  END IF;

  academic_authorized := target_ref IS NOT DISTINCT FROM academic_ref
    AND current_setting('formadig.environment',true) IS NOT DISTINCT FROM 'academic-authorized'
    AND current_setting('formadig.academic_approved',true) IS NOT DISTINCT FROM ns;
  IF NOT academic_authorized AND (
    current_setting('formadig.environment',true) IS DISTINCT FROM 'isolated-development'
    OR current_setting('formadig.development_approved',true) IS DISTINCT FROM ns
    OR target_ref IS NULL OR target_ref !~ '^[a-z0-9]{20}$' OR target_ref=academic_ref) THEN
    RAISE EXCEPTION 'BLOQUEADO: falta aprobación explícita para este destino';
  END IF;
  -- Esta configuración opcional, si existe, aporta una segunda comprobación.
  IF NOT academic_authorized AND coalesce(current_setting('app.settings.supabase_url',true),'') LIKE '%'||academic_ref||'%' THEN
    RAISE EXCEPTION 'BLOQUEADO: DIF requiere autorización académica explícita';
  END IF;
  PERFORM pg_advisory_xact_lock(hashtext(ns));
  -- Dejar explícito el rol: setup administrativo NO constituye una prueba RLS.
  IF current_user NOT IN ('postgres','supabase_admin') THEN
    RAISE EXCEPTION 'El setup requiere el operador de desarrollo autorizado, no un usuario web';
  END IF;

  -- Dependencias Auth: sólo cuentas ficticias exactas y marcadas por un operador.
  -- Si no existen, abortar; no inventar UUID de paciente ni falsear auth.users.
  FOR i IN 1..array_length(names,1) LOOP
    SELECT u.id,u.raw_app_meta_data INTO account FROM auth.users u
      WHERE lower(u.email)='fdg-clinical-'||names[i]||'@example.invalid' FOR SHARE;
    IF NOT FOUND THEN RAISE EXCEPTION 'Falta cuenta Auth sintética: %',names[i]; END IF;
    IF account.raw_app_meta_data->>'formadig_fixture' IS DISTINCT FROM ns
       OR account.raw_app_meta_data->>'role' IS DISTINCT FROM roles[i] THEN
      RAISE EXCEPTION 'Cuenta no marcada para este fixture o rol confiable incorrecto: %',names[i];
    END IF;
    account_ids := array_append(account_ids,account.id);
  END LOOP;
  SELECT array_agg(md5(ns||':psicologia:'||n)::uuid ORDER BY n) INTO psych_ids FROM generate_series(1,26) n;
  SELECT array_agg(md5(ns||':dentista:'||n)::uuid ORDER BY n) INTO dental_ids FROM generate_series(1,26) n;

  IF action IN ('clean','clean_profiles') THEN
    -- La pertenencia de los UUID se verifica bajo bloqueo, no antes de él.
    LOCK TABLE public.modulo_psicologia,public.modulo_dental,public.perfiles IN SHARE ROW EXCLUSIVE MODE;
  END IF;

  -- Comprobar colisiones antes de insertar o limpiar. No depender de un texto
  -- clínico editable como marca de pertenencia: ID + relaciones reservadas.
  FOR i IN 1..26 LOOP
    patient := account_ids[6 + (i % 2)];
    FOREACH module_name IN ARRAY ARRAY['psicologia','dentista'] LOOP
      table_name := CASE WHEN module_name='psicologia' THEN 'modulo_psicologia' ELSE 'modulo_dental' END;
      record_id := CASE WHEN module_name='psicologia' THEN psych_ids[i] ELSE dental_ids[i] END;
      professional := CASE WHEN module_name='psicologia' THEN account_ids[2] ELSE account_ids[3] END;
      EXECUTE format('SELECT paciente_id,atendido_por FROM public.%I WHERE id=$1',table_name)
        INTO actual USING record_id;
      IF actual.paciente_id IS NOT NULL AND
        (actual.paciente_id IS DISTINCT FROM patient OR actual.atendido_por IS DISTINCT FROM professional) THEN
        RAISE EXCEPTION 'Colisión de fixture: %. No se modificó el registro.',record_id;
      END IF;
    END LOOP;
  END LOOP;

  IF action='seed' THEN
    FOR i IN 1..array_length(names,1) LOOP
      IF EXISTS (SELECT 1 FROM public.perfiles p WHERE p.nombre_usuario='fdg-clinical-'||names[i]
                  AND p.id<>account_ids[i]) THEN
        RAISE EXCEPTION 'Nombre reservado ya pertenece a otro perfil';
      END IF;
      INSERT INTO public.perfiles(id,nombre_usuario,nombre_completo,rol,fecha_creacion)
      VALUES(account_ids[i],'fdg-clinical-'||names[i],'FORMADIG TEST '||names[i],roles[i],'2026-10-01T00:00:00Z')
      ON CONFLICT(id) DO UPDATE SET nombre_usuario=EXCLUDED.nombre_usuario,
        nombre_completo=EXCLUDED.nombre_completo,rol=EXCLUDED.rol;
    END LOOP;
    FOR i IN 1..fixture_count LOOP
      patient := account_ids[6+(i%2)];
      INSERT INTO public.modulo_psicologia(id,paciente_id,atendido_por,tipo_atencion,
        motivo_consulta,diagnostico_inicial,numero_sesion,estatus_caso,fecha_sesion)
      VALUES(psych_ids[i],patient,account_ids[2],'Individual',ns||' Psicología expediente '||i,
        'Nota completamente ficticia',i,'En proceso',timestamptz '2026-10-01T15:00:00Z'+make_interval(days=>i-1))
      ON CONFLICT(id) DO NOTHING;
      INSERT INTO public.modulo_dental(id,paciente_id,atendido_por,motivo_consulta,
        diagnostico,tratamiento_realizado,costo_recuperacion,fecha_atencion)
      VALUES(dental_ids[i],patient,account_ids[3],ns||' Dentista expediente '||i,
        'Diagnóstico ficticio','Tratamiento ficticio',(i*10+0.50)::numeric(10,2),
        timestamptz '2026-10-01T16:00:00Z'+make_interval(days=>i-1))
      ON CONFLICT(id) DO NOTHING;
    END LOOP;
    RAISE NOTICE 'Fixtures preparados. Repetir seed no restablece el seguimiento clínico existente.';
  ELSE
    -- Bloquear escrituras concurrentes en padres/hijos durante la comprobación
    -- de dependencias y limpieza, para no crear una ventana de cascadas ajenas.
    FOR fk IN SELECT DISTINCT n.nspname AS source_schema,r.relname AS source_table
      FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace
      WHERE c.contype='f' AND (c.confrelid IN ('public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
        OR (action='clean_profiles' AND c.confrelid='public.perfiles'::regclass))
      ORDER BY n.nspname,r.relname
    LOOP
      EXECUTE format('LOCK TABLE %I.%I IN SHARE ROW EXCLUSIVE MODE',fk.source_schema,fk.source_table);
    END LOOP;
    -- No disparar cascadas hacia tablas nuevas/desconocidas que referencien
    -- estos expedientes. Si hay dependencias, exigir revisión manual.
    FOR fk IN SELECT c.*, n.nspname AS source_schema,r.relname AS source_table,a.attname AS source_column
      FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid
      JOIN pg_namespace n ON n.oid=r.relnamespace
      JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
      WHERE c.contype='f' AND c.confrelid IN ('public.modulo_psicologia'::regclass,'public.modulo_dental'::regclass)
    LOOP
      IF cardinality(fk.conkey)<>1 THEN RAISE EXCEPTION 'FK compuesta: limpieza requiere revisión'; END IF;
      EXECUTE format('SELECT EXISTS(SELECT 1 FROM %I.%I WHERE %I=ANY($1))',fk.source_schema,fk.source_table,fk.source_column)
        INTO found_external USING CASE WHEN fk.confrelid='public.modulo_psicologia'::regclass THEN psych_ids ELSE dental_ids END;
      IF found_external THEN RAISE EXCEPTION 'Dependencia externa a expediente: limpieza cancelada'; END IF;
    END LOOP;
    DELETE FROM public.modulo_psicologia WHERE id=ANY(psych_ids);
    DELETE FROM public.modulo_dental WHERE id=ANY(dental_ids);
    IF action='clean_profiles' THEN
      FOR fk IN SELECT c.*,n.nspname AS source_schema,r.relname AS source_table,a.attname AS source_column
        FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace
        JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
        WHERE c.contype='f' AND c.confrelid='public.perfiles'::regclass
      LOOP
        IF cardinality(fk.conkey)<>1 THEN RAISE EXCEPTION 'FK compuesta: limpieza requiere revisión'; END IF;
        EXECUTE format('SELECT EXISTS(SELECT 1 FROM %I.%I WHERE %I=ANY($1))',fk.source_schema,fk.source_table,fk.source_column)
          INTO found_external USING account_ids;
        IF found_external THEN RAISE EXCEPTION 'Perfiles con otras referencias: transacción cancelada'; END IF;
      END LOOP;
      DELETE FROM public.perfiles WHERE id=ANY(account_ids);
    END IF;
    RAISE NOTICE 'Limpieza limitada completada; cuentas Auth sintéticas conservadas.';
  END IF;
END;
$fixtures$;
COMMIT;
