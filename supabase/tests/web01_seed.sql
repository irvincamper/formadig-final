-- PREPARADO, NO EJECUTADO EN DIF. SQL Editor: propietario administrativo.
-- SET formadig.fixture_approved='web01';
-- SET formadig.test_patient='<UUID de la cuenta ADMIN NUEVA de prueba>';
-- SET formadig.test_psychologist='<UUID de la cuenta PSICOLOGO NUEVA de prueba>';
-- SET formadig.test_dentist='<UUID de la cuenta DENTISTA NUEVA de prueba>';
-- No inserta identidades, perfiles ni roles. No modifica filas existentes.
BEGIN;
DO $$
DECLARE patient uuid; psychologist uuid; dentist uuid; t text; batch int; i int; rid uuid;
BEGIN
 IF current_setting('formadig.fixture_approved',true) IS DISTINCT FROM 'web01' THEN
  RAISE EXCEPTION 'Falta aprobación explícita de datos sintéticos';
 END IF;
 patient:=current_setting('formadig.test_patient')::uuid;
 psychologist:=current_setting('formadig.test_psychologist')::uuid;
 dentist:=current_setting('formadig.test_dentist')::uuid;
 IF (SELECT role FROM formadig_private.web_roles WHERE user_id=patient) IS DISTINCT FROM 'admin'
 OR (SELECT role FROM formadig_private.web_roles WHERE user_id=psychologist) IS DISTINCT FROM 'psicologo'
 OR (SELECT role FROM formadig_private.web_roles WHERE user_id=dentist) IS DISTINCT FROM 'dentista'
 OR (SELECT count(*) FROM public.perfiles WHERE id IN (patient,psychologist,dentist))<>3 THEN
  RAISE EXCEPTION 'Seleccionar únicamente las tres cuentas de prueba aprobadas con perfil vinculado';
 END IF;
 -- Espacio reservado exacto; una segunda ejecución aborta y revierte toda la transacción.
 -- No ON CONFLICT DO UPDATE: nunca sobrescribir un registro que ya exista.
 FOR batch IN 1..6 LOOP
  FOR i IN 1..30 LOOP
   rid:=('75000000-0000-0000-'||lpad(batch::text,4,'0')||'-'||lpad(i::text,12,'0'))::uuid;
   IF batch=1 THEN
    INSERT INTO public.traslados(id,registrado_por,paciente_nombre,paciente_curp,destino_hospital,fecha_viaje,hora_cita,estatus)
    VALUES(rid,patient,'WEB01 FICTICIO '||i,'WEB01FICTICIO'||lpad(i::text,6,'0'),'WEB01 LAB',DATE '2026-10-23'+i,'10:00','Pendiente');
   ELSIF batch IN (2,3,4) THEN
    t:=CASE batch WHEN 2 THEN 'desayunos_frios' WHEN 3 THEN 'desayunos_calientes' ELSE 'desayunos_eaeyd' END;
    EXECUTE format('INSERT INTO public.%I(id,registrado_por,nombres,apellidos,curp,localidad,estatus)
      VALUES($1,$2,$3,$4,$5,$6,$7)',t)
    USING rid,patient,'WEB01 FICTICIO '||i,'PRUEBA SIN BENEFICIARIO','WEB01FICTICIO'||lpad(i::text,6,'0'),'WEB01 LAB','Pendiente';
   ELSIF batch=5 THEN
    INSERT INTO public.modulo_psicologia(id,paciente_id,atendido_por,tipo_atencion,motivo_consulta,numero_sesion,fecha_sesion,estatus_caso)
    VALUES(rid,patient,psychologist,'Individual','WEB01 FICTICIO '||i,i,TIMESTAMPTZ '2026-10-23 10:00Z'+i*INTERVAL '1 minute','Activo');
   ELSE
    INSERT INTO public.modulo_dental(id,paciente_id,atendido_por,motivo_consulta,fecha_atencion,costo_recuperacion)
    VALUES(rid,patient,dentist,'WEB01 FICTICIO '||i,TIMESTAMPTZ '2026-10-23 10:00Z'+i*INTERVAL '1 minute',0);
   END IF;
  END LOOP;
 END LOOP;
END $$;
COMMIT;
