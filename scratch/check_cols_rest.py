import urllib.request
import json
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

url = f"{SUPABASE_URL}/rest/v1/desayunos_calientes?select=*&limit=1"
req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        if data:
            print(json.dumps(list(data[0].keys()), indent=2))
        else:
            print("No data")
except Exception as e:
    print(f"Error: {e}")
