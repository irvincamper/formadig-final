from supabase import create_client

url = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
key = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
supabase = create_client(url, key)

tables = ['desayunos_frios', 'desayunos_fríos', 'desayunos_calientes', 'desayunos_eaeyd', 'traslados', 'hospitales']

for t in tables:
    try:
        res = supabase.table(t).select("*", count="exact").limit(1).execute()
        print(f"Table {t}: {res.count} rows")
        if res.count > 0:
            print(f"Sample row: {res.data[0]}")
    except Exception as e:
        print(f"Table {t}: ERROR - {str(e)}")
