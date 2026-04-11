import os
import shutil

src = r"C:\Users\erick\Downloads\Formadig\Formadig\1_Sistema_DIF_Acatlan"
dst = r"C:\Users\erick\Downloads\Formadig (2)\Formadig\1_Sistema_DIF_Acatlan"

print(f"Buscando HTMLs en {src} y restaurándolos en {dst}...")

count = 0
for dp, dn, files in os.walk(src):
    for f in files:
        if f.endswith('.html'):
            src_file = os.path.join(dp, f)
            rel_path = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel_path)
            
            # Crear directorio destino si no existe
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            
            # Copiar archivo
            shutil.copy2(src_file, dst_file)
            count += 1
            print(f"  -> Restaurado: {rel_path}")

print(f"Total restaurados: {count}")
