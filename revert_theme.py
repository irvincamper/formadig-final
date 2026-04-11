import re
import os

log_path = r'C:\Users\erick\.gemini\antigravity\brain\eccbedc2-566b-4231-af9b-361f35361cd5\.system_generated\logs\overview.txt'

with open(log_path, 'r', encoding='utf-8') as f:
    log_content = f.read()

def extract_old_file(file_path):
    print(f'Extracting {file_path}')
    # The format in the log is exactly:
    # File Path: `file:///c:/Users/erick/Downloads/Formadig/dif_acatlan_system/css/main.css`
    search_path = file_path.replace("\\", "/")
    marker = f"File Path: `file:///{search_path}`"
    
    parts = log_content.split(marker)
    if len(parts) > 1:
        content_part = parts[1]
        
        lines = []
        for line in content_part.split('\n'):
            match = re.match(r'^\d+: (.*)$', line)
            if match:
                lines.append(match.group(1))
            elif 'The above content shows' in line or 'Please note that' in line:
                if lines: # if we found lines, stop.
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
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\dashboard.html",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\modulos\login\vistas\login.html",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\core\core.js",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_system\modulos\login\diseno\login.css",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\index.css",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\LoginScreen.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\AdminDashboard.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\TrasladosDashboard.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\BreakfastsDashboard.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\NutritionDashboard.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\AppointmentsDashboard.tsx",
    r"c:\Users\erick\Downloads\Formadig\dif_acatlan_web_app\src\pages\ReportsDashboard.tsx"
]

for f in files_to_restore:
    extract_old_file(f)

print("Done restoring files if they were found.")
