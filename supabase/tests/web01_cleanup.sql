-- PREPARADO, NO EJECUTADO EN DIF. Mismas variables de sesión que web01_seed.sql.
-- Sólo retira los 180 UUID reservados, con marcador y propietario coincidentes.
BEGIN;
DO $$
DECLARE patient uuid; professional uuid; batch int; t text; marker text; ownercol text;
BEGIN
 IF current_setting('formadig.fixture_approved',true) IS DISTINCT FROM 'web01' THEN
  RAISE EXCEPTION 'Falta aprobación explícita de limpieza WEB01';
 END IF;
 patient:=current_setting('formadig.test_patient')::uuid;
 FOR batch IN 1..6 LOOP
  t:=(ARRAY['traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','modulo_psicologia','modulo_dental'])[batch];
  marker:=CASE WHEN batch=1 THEN 'paciente_nombre' WHEN batch<=4 THEN 'nombres' ELSE 'motivo_consulta' END;
  ownercol:=CASE WHEN batch<=4 THEN 'registrado_por' ELSE 'paciente_id' END;
  professional:=CASE batch WHEN 5 THEN current_setting('formadig.test_psychologist')::uuid
                            WHEN 6 THEN current_setting('formadig.test_dentist')::uuid ELSE NULL END;
  EXECUTE format('DELETE FROM public.%I WHERE id IN
    (SELECT (''75000000-0000-0000-''||lpad($1::text,4,''0'')||''-''||lpad(i::text,12,''0''))::uuid FROM generate_series(1,30) i)
    AND %I=$2 AND %I LIKE ''WEB01 FICTICIO %%'' %s',t,ownercol,marker,
    CASE WHEN batch>=5 THEN 'AND atendido_por=$3' ELSE '' END)
  USING batch,patient,professional;
 END LOOP;
END $$;
COMMIT;
