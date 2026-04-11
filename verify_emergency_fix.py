#!/usr/bin/env python3
"""
FORMADIG System Verification Script
Run this to verify all fixes are working correctly
"""

import os
import sys

print("=" * 80)
print("FORMADIG - Emergency Fix Verification")
print("=" * 80)

# ===== CHECK 1: Verify .env file exists =====
print("\n[CHECK 1] Verifying .env file...")
env_path = ".env"
if os.path.exists(env_path):
    print(f"✅ .env file found at: {os.path.abspath(env_path)}")
    with open(env_path, 'r') as f:
        lines = [l for l in f.readlines() if not l.startswith('#')]
        for line in lines:
            if '=' in line:
                key, _ = line.split('=', 1)
                print(f"   ✓ {key.strip()} = [configured]")
else:
    print(f"❌ .env file NOT found")
    print(f"   Create it at: {os.path.abspath(env_path)}")
    print(f"   With contents:")
    print(f"   SUPABASE_URL=<your_url>")
    print(f"   SUPABASE_KEY=<your_key>")
    print(f"   PORT=10000")
    sys.exit(1)

# ===== CHECK 2: Verify Python dependencies =====
print("\n[CHECK 2] Checking Python dependencies...")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'flask-cors',
    'dotenv': 'python-dotenv',
    'supabase': 'supabase'
}

missing = []
for pkg_name, display_name in required_packages.items():
    try:
        __import__(pkg_name)
        print(f"✅ {display_name} installed")
    except ImportError:
        print(f"❌ {display_name} NOT installed")
        missing.append(display_name)

if missing:
    print(f"\n   Install missing packages:")
    print(f"   pip install {' '.join(missing)}")

# ===== CHECK 3: Verify HTML files exist =====
print("\n[CHECK 3] Verifying module HTML files...")
html_files = [
    "dif_acatlan_system/modulos/admin_traslados/vistas/admin_traslados.html",
    "dif_acatlan_system/modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html",
    "dif_acatlan_system/modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html",
    "dif_acatlan_system/modulos/login/vistas/login.html"
]

for html_file in html_files:
    if os.path.exists(html_file):
        print(f"✅ {html_file}")
    else:
        print(f"❌ {html_file} NOT FOUND")

# ===== CHECK 4: Verify JS files updated =====
print("\n[CHECK 4] Verifying JavaScript updates...")
js_checks = {
    "dif_acatlan_system/modulos/admin_traslados/logica/admin_traslados.js": "hora_salida",
    "dif_acatlan_system/modulos/admin_desayunos_frios/logica/admin_desayunos_frios.js": "df_localidad",
    "dif_acatlan_system/modulos/admin_desayunos_calientes/logica/admin_desayunos_calientes.js": "dc_localidad"
}

for js_file, search_text in js_checks.items():
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {os.path.basename(js_file)} - contains '{search_text}'")
            else:
                print(f"⚠️  {os.path.basename(js_file)} - missing '{search_text}'")
    else:
        print(f"❌ {js_file} NOT FOUND")

# ===== CHECK 5: Verify run.py updated =====
print("\n[CHECK 5] Verifying run.py updates...")
if os.path.exists("run.py"):
    with open("run.py", 'r') as f:
        content = f.read()
        if "load_dotenv" in content:
            print(f"✅ run.py has load_dotenv() function")
        else:
            print(f"⚠️  run.py might not load .env file")
else:
    print(f"❌ run.py NOT FOUND")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

print("""
✅ If all checks passed:
   1. Run: python run.py
   2. Open: http://localhost:10000
   3. Login should work without connection errors
   4. Module location fields should auto-populate

❌ If any checks failed:
   1. Review the error messages above
   2. Install missing packages if needed
   3. Ensure all files were properly created/modified
   4. Check git diff for unexpected changes

📝 For detailed information, see: EMERGENCY_FIX_COMPLETION_REPORT.md
""")
