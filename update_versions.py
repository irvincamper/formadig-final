import os
import re

base_dir = r"c:\Users\erick\Downloads\Formadig (2)\Formadig\1_Sistema_DIF_Acatlan"

# Encontrar todos los .html recursivamente
html_files = []
for root, dirs, files in os.walk(base_dir):
    for name in files:
        if name.endswith(".html"):
            html_files.append(os.path.join(root, name))

print(f"Buscando en: {base_dir}")
print(f"Encontrados {len(html_files)} archivos HTML")

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar ?v=... por ?v=99
        new_content = re.sub(r'\?v=\d+', '?v=99', content)
        
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Actualizado: {os.path.relpath(filepath, base_dir)}")
        else:
            print(f"Sin cambios: {os.path.relpath(filepath, base_dir)}")
            
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")
