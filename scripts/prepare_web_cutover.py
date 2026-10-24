"""Prepara dos archivos privados de ejecución. NO conecta ni aplica SQL."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PHASES=[('B','security_cutover','20261023202914_formadig_rls_corte_coordinado.sql'),
        ('legacy','legacy_cutover','20261024012430_formadig_rls_modulos_legacy.sql')]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backup',type=Path,required=True)
    args=p.parse_args()
    backup=args.backup.resolve()
    if backup.is_relative_to(ROOT):raise RuntimeError('El respaldo debe estar fuera de Git')
    manifest=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
    result=json.loads((backup/'restore-result.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256((backup/'security_schema.dump').read_bytes()).hexdigest()
    if manifest['restore_test']!='passed' or digest!=manifest['sha256'] or result['backup_sha256']!=digest:
        raise RuntimeError('Respaldo/restauración sin validar o hash distinto')
    output=backup/'cutover-prepared'
    output.mkdir(exist_ok=True)
    files={}
    for name,setting,filename in PHASES:
        source=(ROOT/'supabase/migrations'/filename).read_bytes()
        text=source.decode('utf-8')
        (output/(name+'.exec.sql')).write_text("-- Preparado, NO ejecutado. Requiere autorización del prompt final.\nSET formadig."+setting+"='approved';\n"+text,encoding='utf-8')
        files[filename]=hashlib.sha256(source).hexdigest()
    (output/'manifest.json').write_text(json.dumps({'backup_sha256':digest,'migration_sha256':files,'executed':False},indent=2),encoding='utf-8')
    print(json.dumps({'prepared_phases':list(files),'executed':False}))


if __name__=='__main__':main()
