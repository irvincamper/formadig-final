import re
import os
import sys

log_path = r'C:\Users\erick\.gemini\antigravity\brain\4607e7b8-851e-4487-bece-124079382684\.system_generated\logs\overview.txt'

if not os.path.exists(log_path):
    print("Log not found.")
    sys.exit(1)

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    log_content = f.read()

def extract_old_file(file_path):
    print(f'Extracting {file_path}')
    search_path = file_path.replace("\\", "/")
    marker = f"File Path: `file:///{search_path}`"
    
    parts = log_content.split(marker)
    if len(parts) > 1:
        # We want the LAST occurrence because the agent might have updated it!
        # Actually, let's just get the last part to get the final state of that conversation.
        content_part = parts[-1]
        
        lines = []
        for line in content_part.split('\n'):
            match = re.match(r'^\d+: (.*)$', line)
            if match:
                lines.append(match.group(1))
            elif 'The above content shows' in line or 'Please note that' in line:
                if lines:
                    break
        
        if lines:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f'Restored {file_path}')
        else:
            print(f'Failed to parse lines for {file_path}')
    else:
        print(f'Could not find {file_path} in logs')

files_to_restore = [
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\css\main.css",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\css\dashboard.css",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\css\modules.css",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\core\core.js"
]

for f in files_to_restore:
    extract_old_file(f)
