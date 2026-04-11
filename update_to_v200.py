import os
import re

# Usar ruta relativa para mayor portabilidad
base_dir = os.path.join("Formadig", "1_Sistema_DIF_Acatlan")

if not os.path.exists(base_dir):
    print(f"Error: No se encuentra el directorio {base_dir} desde {os.getcwd()}")
    exit(1)

html_files = []
for root, dirs, files in os.walk(base_dir):
    for name in files:
        if name.endswith(".html"):
            html_files.append(os.path.join(root, name))

print(f"Buscando archivos HTML en: {base_dir}")
print(f"Archivos encontrados: {len(html_files)}")

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Cambiar core.js por formadig-core.js?v=201
        new_content = content.replace("core.js", "formadig-core.js")
        
        # 2. Asegurar que la versión sea v=201 para forzar la carga
        new_content = re.sub(r'formadig-core\.js\?v=\d+', 'formadig-core.js?v=201', new_content)
        
        # Si no tenía versión, agregarla
        if "formadig-core.js" in new_content and "v=201" not in new_content:
             new_content = new_content.replace("formadig-core.js", "formadig-core.js?v=201")

        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"OK: {os.path.relpath(filepath, base_dir)}")
            
    except Exception as e:
        print(f"Error en {filepath}: {e}")
