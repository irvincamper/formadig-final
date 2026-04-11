import os
import re

# Encontrar todos los .html recursivamente desde el directorio actual
html_files = []
for root, dirs, files in os.walk("."):
    for name in files:
        if name.endswith(".html"):
            html_files.append(os.path.join(root, name))

print(f"Buscando en: {os.getcwd()}")
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
            print(f"Actualizado: {filepath}")
        else:
            print(f"Sin cambios: {filepath}")
            
    except Exception as e:
        print(f"Error procesando {filepath}: {e}")
