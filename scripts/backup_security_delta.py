"""Respaldo DDL privado por CLI y pg_dump nativo. Nunca exporta filas clínicas.

No restaura producción. El archivo custom contiene esquema, ACL, RLS y funciones.
La recuperación del delta DDL preserva las filas existentes, que B/legacy no modifican.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


def connection(destination):
    result = subprocess.run(['npx.cmd' if os.name == 'nt' else 'npx', '--yes', 'supabase',
                             'db', 'dump', '--linked', '--schema', 'public,formadig_private,auth',
                             '--dry-run'], cwd=ROOT, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', creationflags=FLAGS, timeout=90)
    (destination / 'cli.private.log').write_text(result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('CLI no obtuvo conexión; consultar log privado')
    env = {k: v for k, v in os.environ.items() if not k.startswith('PG')}
    for key, value in re.findall(r'^export (PG[A-Z_]+)=(.*)$', result.stdout, re.M):
        env[key] = shlex.split(value)[0]
    if not all(env.get(k) for k in ('PGHOST', 'PGUSER', 'PGPASSWORD', 'PGDATABASE')):
        raise RuntimeError('Formato de conexión CLI no reconocido')
    # Mismo SET ROLE que utiliza el script oficial generado por Supabase CLI.
    env.update(PGSSLMODE='require', PGCONNECT_TIMEOUT='15',
               PGOPTIONS='-c role=postgres -c default_transaction_read_only=on')
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pg-bin', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.is_relative_to(ROOT) or destination.exists():
        raise RuntimeError('Usar un directorio NUEVO privado fuera del repositorio')
    destination.mkdir(parents=True)
    if os.name == 'nt':
        who = subprocess.check_output(['whoami'], text=True).strip()
        subprocess.run(['icacls', str(destination), '/inheritance:r', '/grant:r', who + ':(OI)(CI)F'],
                       check=True, capture_output=True, creationflags=FLAGS)
    env = connection(destination)
    binary = lambda name: str(args.pg_bin / (name + ('.exe' if os.name == 'nt' else '')))
    def run(name, arguments, output=None):
        result = subprocess.run([binary(name), *arguments], env=env, capture_output=True,
                                creationflags=FLAGS, timeout=180)
        (destination / (name + '.private.log')).write_bytes(result.stderr)
        if result.returncode:
            raise RuntimeError(name + ' falló; consultar log privado')
        if output:
            (destination / output).write_bytes(result.stdout)
        return result.stdout
    version = run('psql', ['-X', '-At', '-c', 'SHOW server_version']).decode().strip()
    archive = destination / 'security_schema.dump'
    run('pg_dump', ['--role=postgres', '--format=custom', '--schema-only', '--schema=public',
                   '--schema=formadig_private', '--schema=auth', '--schema=extensions',
                   '--file=' + str(archive), '--lock-wait-timeout=10s'])
    toc = run('pg_restore', ['--list', str(archive)], 'security_schema.list').decode('utf-8')
    if archive.stat().st_size == 0 or 'TABLE DATA' in toc:
        raise RuntimeError('Respaldo inválido o contiene datos no autorizados')
    run('pg_restore', ['--file=' + str(destination / 'security_schema.sql'), str(archive)])
    query = """SELECT json_build_object(
      'roles',(SELECT json_agg(json_build_object('name',rolname,'inherit',rolinherit,'bypassrls',rolbypassrls)) FROM pg_roles),
      'extensions',(SELECT json_agg(json_build_object('name',extname,'schema',extnamespace::regnamespace::text)) FROM pg_extension),
      'tables',(SELECT json_agg(json_build_object('name',c.relname,'schema',n.nspname,'rls',c.relrowsecurity,'acl',c.relacl))
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','formadig_private') AND c.relkind='r'),
      'policies',(SELECT json_agg(p) FROM pg_policies p WHERE schemaname IN ('public','formadig_private')),
      'constraints',(SELECT json_agg(json_build_object('table',conrelid::regclass::text,'name',conname,'definition',pg_get_constraintdef(oid)))
        FROM pg_constraint WHERE connamespace='public'::regnamespace),
      'columns',(SELECT json_agg(c) FROM information_schema.columns c WHERE table_schema='public'),
      'identity_counts',(SELECT json_build_object('managed',count(*),'mismatches',count(*) FILTER
        (WHERE r.role IS DISTINCT FROM p.rol OR r.role IS DISTINCT FROM u.raw_app_meta_data->>'role'))
        FROM formadig_private.web_roles r LEFT JOIN auth.users u ON u.id=r.user_id LEFT JOIN public.perfiles p ON p.id=r.user_id),
      'migration_history',(SELECT json_agg(version ORDER BY version) FROM supabase_migrations.schema_migrations))"""
    raw = run('psql', ['-X', '-qAt', '-c', 'SET ROLE postgres; ' + query], 'metadata.private.json')
    metadata = json.loads(raw)
    manifest = {'server_version': version, 'archive_bytes': archive.stat().st_size,
                'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'contains_row_data': False, 'scope': 'DDL public/formadig_private/auth/extensions; no clinical/Auth row exports',
                'identities': metadata['identity_counts'], 'restore_test': 'pending'}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
