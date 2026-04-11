from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test 1: Query without accent
        print("Checking 'desayunos_frios' (without accent)...")
        try:
            res = supabase.table('desayunos_frios').select('*').limit(1).execute()
            if res.data:
                print(f"SUCCESS! Found data in 'desayunos_frios': {json.dumps(res.data[0], indent=2)}")
            else:
                print("Connected but no data found in 'desayunos_frios'.")
        except Exception as e:
            print(f"Error 'desayunos_frios': {e}")

        # Test 2: Query with accent
        print("\nChecking 'desayunos_fríos' (with accent)...")
        try:
            res = supabase.table('desayunos_fríos').select('*').limit(1).execute()
            if res.data:
                print(f"SUCCESS! Found data in 'desayunos_fríos': {json.dumps(res.data[0], indent=2)}")
            else:
                print("Connected but no data found in 'desayunos_fríos'.")
        except Exception as e:
            print(f"Error 'desayunos_fríos': {e}")
            
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
