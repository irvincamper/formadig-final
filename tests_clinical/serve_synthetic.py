"""Servidor manual de demostración: sólo memoria, localhost, ninguna conexión Supabase.

Ejecutar: python -m tests_clinical.serve_synthetic
Token exclusivo de este fake: synthetic-admin. Nunca es válido en la aplicación real.
"""
from pathlib import Path
from flask import make_response
from tests_clinical.fakes import synthetic_app, sample
from clinical.validation import SCHEMAS, validate_payload

root = Path(__file__).resolve().parents[1] / 'Formadig' / '1_Sistema_DIF_Acatlan'
app, store = synthetic_app(str(root))
app.config.update(TESTING=False, CLINICAL_ENABLE_UPDATES=False)
for kind in SCHEMAS:
    repo = app.config['CLINICAL_REPOSITORY_FACTORY']('synthetic-admin')
    data = validate_payload(kind, sample(kind))
    data['atendido_por'] = '00000000-0000-0000-0000-000000000001'
    repo.create(kind, data)


@app.get('/api/auth/me')
def synthetic_identity():
    from clinical.security import request_identity
    from clinical.validation import ClinicalError
    from flask import jsonify
    try:
        token, identity, profile, role = request_identity()
        return jsonify(role=role, nombre_completo='Cuenta sintética')
    except ClinicalError as error:
        return jsonify(error=error.message), error.status


@app.get('/demo')
def demo():
    return make_response('''<!doctype html><html lang="es"><title>Demo sintética FORMADIG</title>
    <h1>Demo local: sólo datos sintéticos en memoria</h1>
    <p>Paciente de prueba: 00000000-0000-0000-0000-000000000002</p>
    <button id="start" data-role="admin">Admin General</button>
    <button data-role="psicologo">Psicólogo</button>
    <button data-role="dentista">Dentista</button>
    <a href="/modulos/admin_psicologia/vistas/admin_psicologia.html">Psicología</a>
    <a href="/modulos/admin_dentista/vistas/admin_dentista.html">Dentista</a>
    <script>document.querySelectorAll('[data-role]').forEach(button=>button.onclick=()=>{
    const role=button.dataset.role;
    localStorage.setItem('supabase_token',role==='admin'?'synthetic-admin':role);
    localStorage.setItem('user_role',role);localStorage.setItem('user_fullname','Cuenta sintética');
    button.textContent='Sesión sintética lista: '+role;});</script></html>''')


@app.get('/favicon.ico')
def demo_favicon():
    """La demo no tiene icono; evitar un 404 ajeno a los flujos probados."""
    return '', 204


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable-updates', action='store_true', help='Habilitar seguimiento exclusivamente en memoria sintética')
    parser.add_argument('--enable-creation', action='store_true', help='Permitir altas sólo en el repositorio ficticio en memoria')
    args = parser.parse_args()
    app.config.update(CLINICAL_ENABLE_UPDATES=args.enable_updates,
                      CLINICAL_SYNTHETIC_MODE=True, CLINICAL_ENABLE_CREATION=args.enable_creation)
    app.run(host='127.0.0.1', port=8011, debug=False, use_reloader=False)
