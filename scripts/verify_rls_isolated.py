"""Laboratorio PostgreSQL NUEVO y local; nunca usa URLs ni claves del entorno.

Ejecutar con Python; --pg-bin indica exclusivamente los binarios instalados.
Conserva el directorio temporal detenido para inspección. No conecta a Supabase.
auth.uid/auth.jwt se simulan: valida SQL/RLS real, no Supabase Auth ni JWT reales.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
USER = '00000000-0000-0000-0000-000000000001'
OTHER = '00000000-0000-0000-0000-000000000002'
LEGACY = '00000000-0000-0000-0000-000000000004'

BOOTSTRAP = """
CREATE ROLE anon NOLOGIN;
CREATE ROLE authenticated NOLOGIN;
CREATE SCHEMA auth;
CREATE TABLE auth.users(id uuid PRIMARY KEY,raw_app_meta_data jsonb,raw_user_meta_data jsonb);
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$
 SELECT (current_setting('request.jwt.claims',true)::jsonb->>'sub')::uuid $$;
CREATE FUNCTION auth.jwt() RETURNS jsonb LANGUAGE sql STABLE AS $$
 SELECT current_setting('request.jwt.claims',true)::jsonb $$;
GRANT USAGE ON SCHEMA auth TO anon,authenticated;
CREATE TABLE public.perfiles(id uuid PRIMARY KEY REFERENCES auth.users(id),nombre_usuario text UNIQUE,
 nombre_completo text,apellidos text,rol text,fecha_creacion timestamptz,telefono text,domicilio text,
 clave_elector text,curp text);
CREATE TABLE public.modulo_psicologia(id uuid PRIMARY KEY,paciente_id uuid REFERENCES public.perfiles(id),
 atendido_por uuid REFERENCES public.perfiles(id),tipo_atencion text,motivo_consulta text,
 diagnostico_inicial text,numero_sesion int,estatus_caso text,fecha_sesion timestamptz);
CREATE TABLE public.modulo_dental(id uuid PRIMARY KEY,paciente_id uuid REFERENCES public.perfiles(id),
 atendido_por uuid REFERENCES public.perfiles(id),motivo_consulta text,diagnostico text,
 tratamiento_realizado text,costo_recuperacion numeric(10,2),fecha_atencion timestamptz);
CREATE TABLE public.traslados(id int,registrado_por uuid REFERENCES public.perfiles(id));
ALTER TABLE public.traslados ENABLE ROW LEVEL SECURITY;
GRANT SELECT ON public.traslados TO authenticated;
CREATE POLICY "RLS Traslados" ON public.traslados TO authenticated USING
 (((SELECT perfiles.rol FROM public.perfiles WHERE perfiles.id=auth.uid())='admin_traslados') OR registrado_por=auth.uid());
CREATE FUNCTION public.handle_new_user() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS $$
 BEGIN INSERT INTO public.perfiles(id,rol) VALUES(NEW.id,NEW.raw_user_meta_data->>'rol'); RETURN NEW; END $$;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users
 FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
CREATE POLICY "Insercion automatica" ON public.perfiles FOR INSERT WITH CHECK(true);
CREATE POLICY "Lectura perfiles" ON public.perfiles FOR SELECT USING(true);
CREATE POLICY "Permitir insercion manual perfil" ON public.perfiles FOR INSERT WITH CHECK(true);
CREATE POLICY "Lectura publica modulo_psicologia" ON public.modulo_psicologia FOR SELECT USING(true);
CREATE POLICY "Insercion modulo_psicologia" ON public.modulo_psicologia FOR INSERT WITH CHECK(true);
CREATE POLICY "Lectura publica modulo_dental" ON public.modulo_dental FOR SELECT USING(true);
CREATE POLICY "Insercion modulo_dental" ON public.modulo_dental FOR INSERT WITH CHECK(true);
GRANT ALL ON public.perfiles,public.modulo_psicologia,public.modulo_dental TO anon,authenticated;
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pg-bin', type=Path, required=True)
    args = parser.parse_args()
    bin_dir = args.pg_bin.resolve()
    lab = Path(tempfile.mkdtemp(prefix='formadig-rls-isolated-'))
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('PG')}
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

    def command(name, *arguments):
        with (lab / 'control.log').open('a',encoding='utf8') as log:
            result = subprocess.run([str(bin_dir / (name + ('.exe' if os.name == 'nt' else ''))), *arguments],
                                    env=env, stdout=log, stderr=log,
                                    creationflags=flags, timeout=45)
        if result.returncode:
            raise RuntimeError((lab / 'control.log').read_text(encoding='utf8',errors='replace')[-2000:])

    def sql(query, expect_error=False):
        result = subprocess.run([str(bin_dir / ('psql.exe' if os.name == 'nt' else 'psql')),
                                 '-X', '-h', '127.0.0.1', '-p', str(port), '-U', 'postgres',
                                 '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-At'], input=query,
                                env=env, capture_output=True, text=True, encoding='utf8', errors='replace',
                                creationflags=flags, timeout=20)
        if expect_error:
            assert result.returncode != 0 and ('permission denied' in result.stderr or
                    'row-level security' in result.stderr), result.stderr
        elif result.returncode:
            raise RuntimeError(result.stderr[-2000:])
        return result.stdout

    results = []

    def check(name, query, expected=None, denied=False):
        output = sql(query, expect_error=denied)
        if expected is not None:
            assert expected in output.splitlines(), (name, output, expected)
        results.append({'name': name, 'passed': True})

    def actor(role, query, anonymous=False, db_role='authenticated', user=USER, claim=None):
        claims = json.dumps({'sub': user, 'app_metadata': {'role': claim or role},
                             'user_metadata': {'role': 'admin', 'rol': 'admin'}, 'is_anonymous': anonymous})
        return ("BEGIN; SET LOCAL ROLE " + db_role + "; SELECT set_config('request.jwt.claims','" +
                claims + "',true); " + query + '; ROLLBACK;')

    started = False
    try:
        command('initdb', '-D', str(lab / 'data'), '-U', 'postgres', '--auth=trust', '--encoding=UTF8', '--locale=C')
        # Trust solamente en la instancia temporal ligada a loopback, sin datos reales.
        command('pg_ctl', '-D', str(lab / 'data'), '-l', str(lab / 'postgres.log'),
                '-o', f'-h 127.0.0.1 -p {port}', '-w', 'start')
        started = True
        sql(BOOTSTRAP)
        phase_a = next((ROOT / 'supabase/migrations').glob('*_formadig_roles_protegidos.sql'))
        phase_b = next((ROOT / 'supabase/migrations').glob('*_formadig_rls_corte_coordinado.sql'))
        sql(f"INSERT INTO auth.users VALUES ('{LEGACY}','{{}}','{{\"rol\":\"admin_traslados\"}}');")
        sql(phase_a.read_text(encoding='utf8'))
        check('fase A no migra roles historicos', 'SELECT count(*) FROM formadig_private.web_roles', '0')
        check('fase A conserva perfil historico', f"SELECT rol FROM public.perfiles WHERE id='{LEGACY}'", 'admin_traslados')
        check('autorregistro no copia rol editable', f"INSERT INTO auth.users VALUES ('{OTHER}','{{}}',"
              "'{\"rol\":\"admin\"}'); SELECT count(*) FROM formadig_private.web_roles", '0')
        check('perfil no recibe admin autodeclarado', f"SELECT count(*) FROM public.perfiles WHERE id='{OTHER}' AND rol IS NULL", '1')
        sql(f"INSERT INTO auth.users VALUES ('{USER}','{{\"role\":\"admin\"}}','{{}}');"
            f"INSERT INTO public.modulo_psicologia(id,paciente_id) VALUES ('{USER}','{OTHER}');"
            f"INSERT INTO public.modulo_dental(id,paciente_id) VALUES ('{USER}','{OTHER}');"
            f"INSERT INTO public.traslados VALUES(1,'{USER}'),(2,'{OTHER}');")
        try:
            sql(phase_b.read_text(encoding='utf8'))
            raise AssertionError('Corte sin autorizacion aceptado')
        except RuntimeError as error:
            assert 'Falta aprobar corte coordinado' in str(error), str(error)
            results.append({'name': 'corte exige aprobacion explicita', 'passed': True})
        try:
            sql("SET formadig.security_cutover='approved';\n" + phase_b.read_text(encoding='utf8'))
            raise AssertionError('Corte con cuenta web sin aprovisionar aceptado')
        except RuntimeError as error:
            assert 'Completar revision y aprovisionamiento' in str(error), str(error)
            results.append({'name': 'corte bloquea cuentas web sin revisar', 'passed': True})
        check('preflight fallido no cambia RLS', "SELECT relrowsecurity FROM pg_class WHERE oid='public.perfiles'::regclass", 'f')
        # Aprovisionamiento explícito de fixture, nunca conversión automática de metadatos editables.
        sql(f"UPDATE auth.users SET raw_app_meta_data='{{\"role\":\"admin_traslados\"}}' WHERE id='{LEGACY}';")
        sql("SET formadig.security_cutover='approved';\n" + phase_b.read_text(encoding='utf8'))
        for role in ('admin', 'admin_traslados', 'admin_desayunos', 'psicologo', 'dentista'):
            sql(f"UPDATE auth.users SET raw_app_meta_data='{{\"role\":\"{role}\"}}' WHERE id='{USER}';")
            for table, area in [('modulo_psicologia', 'psicologo'), ('modulo_dental', 'dentista')]:
                check(role + ': SELECT ' + table, actor(role, f'SELECT count(*) FROM public.{table}'),
                      '1' if role in ('admin', area) else '0')
                for verb in ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE'):
                    query = {'INSERT': f"INSERT INTO public.{table}(id) VALUES('{OTHER}')",
                             'UPDATE': f'UPDATE public.{table} SET motivo_consulta=\'x\'',
                             'DELETE': f'DELETE FROM public.{table}', 'TRUNCATE': f'TRUNCATE public.{table}'}[verb]
                    check(role + ': bloquea ' + verb + ' ' + table, actor(role, query), denied=True)
            check(role + ': edita nombre y telefono propios', actor(role,
                  f"UPDATE public.perfiles SET nombre_completo='Self synthetic',telefono='000' WHERE id='{USER}' RETURNING nombre_completo"), 'Self synthetic')
            check(role + ': no puede modificar rol por REST/SQL', actor(role, "UPDATE public.perfiles SET rol='admin'"), denied=True)
            check(role + ': registro protegido', actor(role, "UPDATE formadig_private.web_roles SET role='admin'"), denied=True)
            check(role + ': compatibilidad RLS Traslados', actor(role, 'SELECT count(*) FROM public.traslados'),
                  '2' if role == 'admin_traslados' else '1')
        sql(f"UPDATE auth.users SET raw_app_meta_data='{{\"role\":\"admin\"}}' WHERE id='{USER}';")
        check('admin edita datos no sensibles', actor('admin', f"UPDATE public.perfiles SET nombre_completo='Synthetic' WHERE id='{OTHER}' RETURNING nombre_completo"), 'Synthetic')
        check('admin no borra perfiles en cascada', actor('admin', 'DELETE FROM public.perfiles'), denied=True)
        check('anon no lee clínicas', actor('admin', 'SELECT * FROM public.modulo_dental', db_role='anon'), denied=True)
        check('Auth anónimo no lee clínicas', actor('admin', 'SELECT count(*) FROM public.modulo_dental', anonymous=True), '0')
        sql(f"UPDATE auth.users SET raw_app_meta_data='{{\"role\":\"dentista\"}}' WHERE id='{USER}';")
        check('token admin anterior pierde acceso', actor('dentista', 'SELECT count(*) FROM public.modulo_psicologia', claim='admin'), '0')
        check('token admin anterior no lee todos los perfiles', actor('dentista', 'SELECT count(*) FROM public.perfiles', claim='admin'), '1')
        check('rol editado en user_metadata no concede acceso', actor('dentista', 'SELECT count(*) FROM public.modulo_psicologia'), '0')
        sql(f"UPDATE auth.users SET raw_user_meta_data='{{\"rol\":\"admin\"}}' WHERE id='{USER}';")
        check('editar user_metadata no cambia registro', f"SELECT role FROM formadig_private.web_roles WHERE user_id='{USER}'", 'dentista')
        check('cuenta no web edita solo datos propios', actor('usuario',
              f"UPDATE public.perfiles SET nombre_completo='Non web synthetic' WHERE id='{OTHER}' RETURNING nombre_completo", user=OTHER), 'Non web synthetic')
        check('Auth anonimo no edita perfil', actor('dentista',
              f"UPDATE public.perfiles SET nombre_completo='x' WHERE id='{USER}'", anonymous=True), 'UPDATE 0')
        check('perfil propio y UUID disponibles al dentista', actor('dentista', 'SELECT count(*) FROM public.perfiles'), '1')
        check('dentista no edita otros perfiles', actor('dentista', f"UPDATE public.perfiles SET nombre_completo='x' WHERE id='{OTHER}'"), 'UPDATE 0')
        print(json.dumps({'status': 'passed', 'checks': len(results), 'lab': str(lab),
                          'scope': 'PostgreSQL local; Auth/JWT simulados', 'results': results}, ensure_ascii=True))
    finally:
        if started or (lab / 'data' / 'postmaster.pid').exists():
            command('pg_ctl', '-D', str(lab / 'data'), '-m', 'fast', '-w', 'stop')


if __name__ == '__main__':
    main()
