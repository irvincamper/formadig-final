import os
import re

log_path = r"C:\Users\erick\.gemini\antigravity\brain\36aa6d27-c4b3-416a-94e7-64eeed767eee\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    log_content = f.read()

# Buscamos todas las instancias de view_file
# La estructura suele ser:
# File Path: `file:///...`
# Total Lines: ...
# Showing lines 1 to ...
# The following code has been modified...
# 1: <!DOCTYPE html>
# ...
# 56: 
# The above content shows the entire, complete file contents of the requested file.

pattern = re.compile(r"File Path: `file:///(.*?)`[\s\S]*?Showing lines (\d+) to (\d+)[\s\S]*?<original_line>.*?\n(.*?)The above content (shows|does)", re.DOTALL)

for match in pattern.finditer(log_content):
    file_path_encoded = match.group(1)
    file_path = file_path_encoded.replace('%20', ' ').replace('/', '\\')
    
    if "admin_sms.html" in file_path or "chatbot.html" in file_path or "admin_desayunos_frios.html" in file_path or "admin_espacios_eaeyd.html" in file_path:
        lines_text = match.group(4)
        
        # Extraemos las líneas removiendo "N: "
        clean_lines = []
        for line in lines_text.split('\n'):
            line_match = re.match(r'^\d+: (.*)', line)
            if line_match:
                clean_lines.append(line_match.group(1))
            else:
                if line.strip() != "":
                    pass # ignore unexpected
        
        # Guardamos el archivo si está completo (empieza en 1)
        if match.group(2) == '1':
            try:
                with open("C:\\" + file_path, 'w', encoding='utf-8') as out_f:
                    out_f.write('\n'.join(clean_lines))
                print(f"Recuperado desde logs: {file_path}")
            except Exception as e:
                print(f"Error escribiendo {file_path}: {e}")

