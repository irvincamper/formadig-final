from supabase import create_client
sb = create_client('https://ctiqbycbkcftwuqgzxjb.supabase.co', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')
res = sb.table('traslados').select('id,url_doc_beneficiario,url_doc_acompanante,url_comprobante_domicilio').execute()
print(f'Total registros: {len(res.data)}')
for r in res.data:
    rid = str(r.get('id', '?'))[:8]
    b = bool(r.get('url_doc_beneficiario'))
    a = bool(r.get('url_doc_acompanante'))
    c = bool(r.get('url_comprobante_domicilio'))
    benef_url = r.get('url_doc_beneficiario', '')
    print(f'  ID {rid}... | beneficiario={b} | acompanante={a} | comprobante_dom={c}')
    if benef_url:
        print(f'    -> URL beneficiario: {benef_url[:80]}')
