from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def check_data():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("--- Checking desayunos_eaeyd table ---")
        res = supabase.table('desayunos_eaeyd').select('*').execute()
        print(f"Total records in desayunos_eaeyd: {len(res.data)}")
        
        types = {}
        for r in res.data:
            t = r.get('tipo_apoyo', 'None')
            types[t] = types.get(t, 0) + 1
        
        print(f"Records by tipo_apoyo: {types}")
        
        if res.data:
            print("\nSample record:")
            print(json.dumps(res.data[0], indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
