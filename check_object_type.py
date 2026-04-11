from supabase import create_client, Client

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Intentar llamar a una función que devuelva info de tablas si existe (POCO PROBABLE)
    # Mejor: intentar un query a pg_catalog si el usuario no tiene RLS que lo bloquee
    # En Supabase usualmente no puedes consultar pg_catalog desde el cliente publishable.
    
    # Intentar un select que fuerce un error de sistema que revele si es vista
    res = supabase.table('desayunos_sieb').select('*').limit(0).execute()
    print("SELECT * worked (0 rows).")
except Exception as e:
    print(f"ERROR: {e}")

# Intentar insertar con ABSOLUTAMENTE NADA
try:
    res = supabase.table('desayunos_sieb').insert({}).execute()
    print("INSERT {} worked.")
except Exception as e:
    print(f"INSERT {} ERROR: {e}")
