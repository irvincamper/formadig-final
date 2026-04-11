from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conectado a Supabase - Traslados")
except Exception as e:
    print(f"ATENCIÓN: Error conectando a Supabase: {e}")
    supabase = None

@app.route('/', methods=['GET'])
def obtener_registros():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    try:
        res = supabase.table('traslados').select('*').order('fecha_solicitud', desc=True).execute()
        
        # Mapear columnas reales de DB -> nombres que el frontend espera
        traslados_mapeados = []
        for r in res.data:
            # Combinar fecha/hora de la app móvil con fecha_viaje/hora_cita del esquema original
            fecha_display = r.get('fecha_viaje') or r.get('fecha')
            hora_display  = r.get('hora_cita')  or r.get('hora')

            traslados_mapeados.append({
                # IDs y meta
                "id":                r.get('id'),
                "registrado_por":    r.get('registrado_por'),
                "fecha_solicitud":   r.get('fecha_solicitud'),
                # Paciente
                "paciente_nombre":   r.get('paciente_nombre'),
                "paciente_curp":     r.get('paciente_curp'),
                "paciente_edad":     r.get('paciente_edad'),
                "paciente_domicilio":r.get('paciente_domicilio'),
                "localidad":         r.get('paciente_domicilio'),  # alias
                # Destino
                "destino_hospital":  r.get('destino_hospital'),
                "destino":           r.get('destino_hospital'),    # alias
                # Fecha y hora (compatibilidad doble)
                "fecha_viaje":       r.get('fecha_viaje'),
                "fecha_cita":        fecha_display,                 # frontend usa fecha_cita
                "hora_cita":         r.get('hora_cita'),
                "hora_salida":       hora_display,                  # frontend usa hora_salida
                "fecha":             r.get('fecha'),
                "hora":              r.get('hora'),
                # Contacto
                "telefono_principal":r.get('telefono_principal'),
                "telefono":          r.get('telefono_principal'),   # alias
                "telefono_secundario":r.get('telefono_secundario'),
                "telefono_emergencia":r.get('telefono_secundario'), # alias frontend
                # Identidad oficial
                "clave_elector":     r.get('clave_elector') or r.get('clave_de_elector'),
                # Acompañante
                "acompanante_nombre":r.get('acompanante_nombre'),
                "acompanante_entidad": r.get('acompanante_entidad') or r.get('entidad'),
                "tutor":             r.get('acompanante_nombre'),   # alias
                # Estatus y logística
                "estatus":           r.get('estatus', 'Pendiente'),
                "kilometraje_salida":r.get('kilometraje_salida'),
                "kilometraje_llegada":r.get('kilometraje_llegada'),
                # Documentos (URLs de imágenes de la app móvil)
                "url_doc_beneficiario": r.get('url_doc_beneficiario') or r.get('url_ine_paciente') or r.get('foto_ine_url') or r.get('url_curp') or r.get('url_ine'),
                "url_doc_acompanante":  r.get('url_doc_acompanante') or r.get('url_ine_acompanante') or r.get('url_doc_ine_tutor'),
                "url_foto_infante":      r.get('url_foto_infante') or r.get('foto_paciente') or r.get('url_foto_paciente') or r.get('url_foto'),
                "url_comprobante_domicilio": r.get('url_comprobante_domicilio') or r.get('comprobante_domicilio') or r.get('url_comprobante') or r.get('url_doc_domicilio'),
                "lugares_requeridos":   r.get('lugares_requeridos', 2),
            })

        print(f"📋 GET /api/traslados → {len(traslados_mapeados)} registros")
        return jsonify({"traslados": traslados_mapeados}), 200
    except Exception as e:
        print(f"❌ Error al obtener traslados: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['POST'])
def nuevo_registro():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    required_fields = ['paciente_nombre', 'paciente_curp', 'destino', 'cita_fecha', 'cita_hora']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    try:
        supabase_data = {
            "paciente_nombre":   f"{data.get('paciente_nombre')} {data.get('apellidos', '')}".strip(),
            "paciente_curp":     data.get('paciente_curp'),
            "paciente_domicilio":data.get('localidad'),
            "acompanante_nombre":data.get('tutor') or data.get('acompanante_nombre'),
            "destino_hospital":  data.get('destino'),
            "fecha_viaje":       data.get('cita_fecha'),
            "hora_cita":         data.get('cita_hora'),
            "telefono_principal":data.get('telefono'),
            "estatus":           data.get('estatus', 'Pendiente'),
        }
        res = supabase.table('traslados').insert(supabase_data).execute()
        if res.data:
            print(f"✅ Traslado guardado: ID {res.data[0]['id']}")
        return jsonify({"message": "Traslado guardado exitosamente", "data": res.data[0] if res.data else {}}), 201
    except Exception as e:
        print(f"❌ Error al guardar traslado: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/<string:record_id>', methods=['PUT', 'PATCH'])
def actualizar_traslado(record_id):
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    try:
        target_id = int(record_id) if record_id.isdigit() else record_id

        # Combinamos nombre y apellidos si vienen por separado en el form
        nombre_form = data.get('paciente_nombre', '') or ''
        apell_form  = data.get('apellidos', '') or ''
        nombre_completo_form = f"{nombre_form} {apell_form}".strip()

        update_data = {
            "paciente_nombre":     nombre_completo_form or nombre_form,
            "paciente_curp":       data.get('paciente_curp'),
            "paciente_domicilio":  data.get('localidad'),
            "destino_hospital":    data.get('destino'),
            "fecha_viaje":         data.get('cita_fecha'),
            "hora_cita":           data.get('cita_hora'),
            "telefono_principal":  data.get('telefono'),
            "telefono_secundario": data.get('telefono_emergencia'),
            "acompanante_clave_elector": data.get('clave_elector'),
            "acompanante_nombre":  data.get('tutor'),
            "estatus":             data.get('estatus', 'Programado').strip().upper()
        }
        
        # Limpiar valores None para evitar sobreescribir con nulos si no vienen en el request
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Extraer el JWT enviado desde el frontend
        auth_header = request.headers.get('Authorization')
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=representation" # Para obtener el objeto actualizado
        }
        if auth_header and auth_header.startswith('Bearer '):
            headers["Authorization"] = auth_header
            # Extraer UUID del Token para inyectarlo y evitar crash del trigger si es null
            try:
                import base64, json
                token = auth_header.split(' ')[1]
                payload = token.split('.')[1]
                pad = '=' * (-len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload + pad).decode('utf-8'))
                admin_uuid = decoded.get('sub')
                
                # Fetch el registro actual para ver si le falta el usuario (registros de adm)
                url_get = f"{SUPABASE_URL}/rest/v1/traslados?select=registrado_por&id=eq.{target_id}"
                rg = requests.get(url_get, headers={"apikey": SUPABASE_KEY, "Authorization": auth_header})
                if rg.status_code == 200 and rg.json():
                    if not rg.json()[0].get('registrado_por'):
                        # PRE-PATCH: Asignar usuario primero sin tocar estatus para que OLD.registrado_por ya no sea null
                        url_patch = f"{SUPABASE_URL}/rest/v1/traslados?id=eq.{target_id}"
                        requests.patch(url_patch, json={'registrado_por': admin_uuid}, headers=headers, proxies={"http": None, "https": None})
            except Exception as e:
                print(f"Error parseando JWT / Pre-Patch: {e}")
        else:
            headers["Authorization"] = f"Bearer {SUPABASE_KEY}" # Fallback anon key

        # Hacemos el parche manual para inyectar el token específico del usuario y pasar RLS
        url = f"{SUPABASE_URL}/rest/v1/traslados?id=eq.{target_id}"
        r = requests.patch(url, json=update_data, headers=headers, proxies={"http": None, "https": None})
        
        if r.status_code >= 400:
            return jsonify({"error": f"Supabase rechazó la operación: {r.text}"}), r.status_code

        res_data = r.json()
        if not res_data:
            return jsonify({"error": "⚠️ BLOQUEADO POR SUPABASE: La tabla 'traslados' tiene activado el Row Level Security (RLS) que impide actualizar registros. Ve a tu panel de Supabase > Authentication > Policies y crea una política UPDATE, o desactiva RLS."}), 404
            
        print(f"✅ Traslado actualizado ID: {target_id}")
        
        # --- DISPARAR SMS AUTOMÁTICO AL ACEPTAR ---
        if update_data.get('estatus') == 'ACEPTADO':
            try:
                rec = res_data[0]
                tel = rec.get('telefono_principal') or rec.get('telefono_secundario')
                fecha_v = rec.get('fecha_viaje', '')
                hora_c = rec.get('hora_cita', '')
                if tel:
                    msg_texto = f"DIF Acatlan: Tu traslado esta programado el dia {fecha_v} a las {hora_c}. ¿Confirmas que asistiras ese dia y a la hora acordada? Responde SI o NO."
                    
                    def enviar_sms_async(telefono, mensaje):
                        try:
                            requests.post('http://localhost:5009/api/sms/send', json={
                                'phone': telefono,
                                'message': mensaje,
                                'user_id': 'Bot Traslados'
                            }, timeout=5)
                        except Exception as e:
                            print(f"Error enviando SMS asíncrono: {e}")
                            
                    import threading
                    threading.Thread(target=enviar_sms_async, args=(tel, msg_texto)).start()
                    print(f"📲 Auto-SMS de confirmación disparado para {tel}")
            except Exception as e:
                print(f"Error procesando auto-SMS: {e}")

        return jsonify({"message": f"¡Traslado #{target_id} agendado correctamente!", "data": res_data[0]}), 200
    except Exception as e:
        print(f"❌ Error al actualizar traslado: {e}")
        return jsonify({"error": f"Error de conectividad/servidor: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚑 Servidor Traslados iniciado en puerto 5004 — LISTO CON DATOS MÓVIL")
    app.run(host='0.0.0.0', port=5004, debug=False, use_reloader=False)
