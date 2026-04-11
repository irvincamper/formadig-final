from supabase import create_client

url = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
key = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
supabase = create_client(url, key)

tables_to_check = ["desayunos_sieb", "desayunos_eaeyd", "desayunos_frios", "desayunos_calientes", "eaeyd", "espacios_eaeyd"]

for table in tables_to_check:
    print(f"--- Checking {table} ---")
    try:
        res = supabase.table(table).select("*").limit(1).execute()
        if res.data:
            print(f"Columns: {list(res.data[0].keys())}")
        else:
            print("Empty table")
    except Exception as e:
        print(f"Error: {e}")
