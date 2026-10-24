"""Restaura exclusivamente en un clúster NUEVO loopback; nunca conecta a DIF."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backup', type=Path, required=True)
    p.add_argument('--pg-bin', type=Path, required=True)
    args = p.parse_args()
    backup = args.backup.resolve()
    manifest = json.loads((backup / 'manifest.json').read_text())
    archive = backup / 'security_schema.dump'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['sha256']
    metadata = json.loads((backup / 'metadata.private.json').read_text(encoding='utf-8'))
    # Dentro del árbol privado que contiene el respaldo, no en el repositorio.
    lab = Path(tempfile.mkdtemp(prefix='restore-isolated-', dir=backup))
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('PG')}
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    def command(name, *arguments, query=None):
        binary = args.pg_bin / (name + ('.exe' if os.name == 'nt' else ''))
        # pg_ctl puede heredar pipes hacia postgres en Windows; usar archivos evita
        # esperar indefinidamente a EOF de un servidor que sigue ejecutándose.
        if name == 'pg_ctl':
            with (lab / 'control.private.log').open('a', encoding='utf-8') as control:
                r = subprocess.run([str(binary), *arguments], stdout=control, stderr=control,
                                   env=env, creationflags=flags, timeout=45)
            if r.returncode:
                raise RuntimeError('pg_ctl falló; consultar control.private.log')
            return ''
        r = subprocess.run([str(binary), *arguments], input=query, text=True,
                           encoding='utf-8', errors='replace', capture_output=True,
                           env=env, creationflags=flags, timeout=120)
        with (lab / 'restore.private.log').open('a', encoding='utf-8') as log:
            log.write(r.stderr)
        if r.returncode:
            raise RuntimeError(name + ' falló: revisar log privado de restauración')
        return r.stdout
    connection = ['-h', '127.0.0.1', '-p', str(port), '-U', 'postgres', '-d', 'postgres']
    def sql(q):
        return command('psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', *connection, query=q)
    started = False
    try:
        command('initdb', '-D', str(lab / 'data'), '-U', 'postgres', '--auth=trust', '--encoding=UTF8')
        command('pg_ctl', '-D', str(lab / 'data'), '-l', str(lab / 'server.private.log'),
                '-o', f'-h 127.0.0.1 -p {port}', '-w', 'start')
        started = True
        for role in metadata['roles']:
            name = role['name']
            if name == 'postgres' or name.startswith('pg_'):
                continue
            sql('CREATE ROLE "' + name.replace('"', '""') + '" NOLOGIN ' +
                ('INHERIT' if role['inherit'] else 'NOINHERIT') + ' ' +
                ('BYPASSRLS' if role['bypassrls'] else 'NOBYPASSRLS') + ';')
        sql('DROP SCHEMA public;')  # Clúster vacío creado arriba: nunca remoto.
        command('pg_restore', '--exit-on-error', *connection, str(archive))
        restored = json.loads(sql("""SELECT json_build_object(
          'tables',(SELECT json_agg(json_build_object('name',c.relname,'schema',n.nspname,'rls',c.relrowsecurity,'acl',c.relacl))
          FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','formadig_private') AND c.relkind='r'),
          'policies',(SELECT json_agg(p) FROM pg_policies p WHERE schemaname IN ('public','formadig_private')),
          'constraints',(SELECT json_agg(json_build_object('table',conrelid::regclass::text,'name',conname,'definition',pg_get_constraintdef(oid)))
          FROM pg_constraint WHERE connamespace='public'::regnamespace))"""))
        (lab / 'restored-metadata.private.json').write_text(json.dumps(restored,indent=2))
        for key in ('tables', 'policies', 'constraints'):
            normalize = lambda rows: sorted(json.dumps(x, sort_keys=True) for x in rows)
            assert normalize(metadata[key]) == normalize(restored[key]), 'Diferencia restaurada: ' + key
        # Comprueba que el DDL remoto real acepta las fases con identidades locales sintéticas.
        roles = ['admin']*3 + ['admin_traslados']*4 + ['admin_desayunos']*2 + ['psicologo','dentista']
        for i, role in enumerate(roles, 1):
            uid = '74000000-0000-0000-0000-' + str(i).zfill(12)
            sql("INSERT INTO auth.users(id,raw_app_meta_data,raw_user_meta_data) VALUES('" + uid +
                "','" + json.dumps({'role':role}) + "','" +
                json.dumps({'nombre_usuario':'WEB01_LAB_'+str(i),'nombre_completo':'WEB01 FICTICIO'}) + "');")
        for setting, filename in [
            ('security_cutover','20261023202914_formadig_rls_corte_coordinado.sql'),
            ('legacy_cutover','20261024012430_formadig_rls_modulos_legacy.sql')]:
            migration = (ROOT / 'supabase/migrations' / filename).read_text(encoding='utf-8')
            sql("SET formadig." + setting + "='approved';\n" + migration)
            # Son migraciones de una ejecución, no idempotentes. Repetir debe abortar.
            failed = False
            try:
                sql("SET formadig." + setting + "='approved';\n" + migration)
            except RuntimeError:
                failed = True
            assert failed, 'Repetición inesperadamente aceptada'
        fixture_settings = "SET formadig.fixture_approved='web01'; SET formadig.test_patient='74000000-0000-0000-0000-000000000001'; SET formadig.test_psychologist='74000000-0000-0000-0000-000000000010'; SET formadig.test_dentist='74000000-0000-0000-0000-000000000011';\n"
        sql(fixture_settings + (ROOT / 'supabase/tests/web01_seed.sql').read_text(encoding='utf-8'))
        counts = sql("SELECT (SELECT count(*) FROM public.traslados)+(SELECT count(*) FROM public.desayunos_frios)+(SELECT count(*) FROM public.desayunos_calientes)+(SELECT count(*) FROM public.desayunos_eaeyd)+(SELECT count(*) FROM public.modulo_psicologia)+(SELECT count(*) FROM public.modulo_dental)")
        assert counts.strip() == '180'
        try:
            sql(fixture_settings + (ROOT / 'supabase/tests/web01_seed.sql').read_text(encoding='utf-8'))
        except RuntimeError:
            pass
        else:
            raise AssertionError('Seed repetido debe abortar sin sobrescribir')
        for role, number, table, expected in [('psicologo',10,'modulo_psicologia',30),('dentista',11,'modulo_dental',30),('admin',1,'modulo_dental',0),('admin_traslados',4,'modulo_psicologia',0),('psicologo',10,'traslados',0)]:
            claims=json.dumps({'sub':'74000000-0000-0000-0000-'+str(number).zfill(12),'app_metadata':{'role':role}})
            assert sql("SET request.jwt.claims='"+claims+"'; SET ROLE authenticated; SELECT count(*) FROM public."+table).strip()==str(expected)
        sql(fixture_settings + (ROOT / 'supabase/tests/web01_cleanup.sql').read_text(encoding='utf-8'))
        assert sql('SELECT count(*) FROM public.traslados').strip() == '0'
        assert sql('SELECT count(*) FROM public.modulo_psicologia').strip() == '0'
        sql((ROOT / 'supabase/recovery/formadig_fail_closed.sql').read_text())
        sql((ROOT / 'supabase/recovery/formadig_fail_closed.sql').read_text())
        result = {'status':'passed','backup_sha256':manifest['sha256'],
                  'restored_schema':True,'acl_rls_constraints_match':True,
                  'phase_b_and_legacy_on_restored_schema':True,'replay_aborts':True,
                  'fail_closed_repeated':True,'synthetic_fixture_rows':180,'fixture_seed_cleanup_verified':True,
                  'clinical_or_auth_rows_exported':False,
                  'scope':'DDL recovery; existing production rows are unchanged by the planned cut'}
        (backup / 'restore-result.json').write_text(json.dumps(result, indent=2))
        manifest['restore_test']='passed'
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        print(json.dumps(result))
    finally:
        if started:
            command('pg_ctl', '-D', str(lab / 'data'), '-m', 'fast', '-w', 'stop')


if __name__ == '__main__':
    main()
