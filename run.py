import os
import subprocess
import sys
import webbrowser
import time
import importlib.util
from flask import Flask, send_from_directory, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# En Render/Gunicorn, este módulo se puede usar como WSGI entrypoint.
# `gunicorn run:app` sirve la UI estática y enruta los endpoints /api al backend.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")

front_app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@front_app.route('/', defaults={'path': ''})
@front_app.route('/<path:path>')
def serve_frontend(path):
    # La raíz del sitio redirige directamente a la pantalla de login real.
    if not path:
        return redirect('/modulos/login/vistas/login.html')

    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isdir(full_path):
        return front_app.send_static_file(os.path.join(path, 'index.html'))

    return send_from_directory(FRONTEND_DIR, path)


def _load_wsgi_app():
    backend_path = os.path.join(
        BASE_DIR,
        "Formadig",
        "1_Sistema_DIF_Acatlan",
        "modulos",
        "login",
        "logica",
        "login_backend.py"
    )
    if not os.path.exists(backend_path):
        return None

    try:
        spec = importlib.util.spec_from_file_location("login_backend", backend_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "app", None)
    except Exception as exc:
        print(f"[WARN] No se pudo cargar el app WSGI desde {backend_path}: {exc}")
        return None

backend_app = _load_wsgi_app()
if backend_app is not None:
    app = DispatcherMiddleware(front_app, {'/api': backend_app})
else:
    app = front_app


def kill_ports(ports):
    """Mata eficientemente procesos usando una lista de puertos (Windows/Linux)"""
    current_pid = str(os.getpid())
    if sys.platform == "win32":
        try:
            print(f"   [A] Consultando estado de red (timeout 5s)...")
            cmd = 'netstat -ano | findstr /R "LISTENING ESCUCHANDO"'
            # Añadimos timeout para evitar que el sistema se quede colgado aquí
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5).decode(errors='ignore')
            
            pids_to_kill = set()
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    local_address = parts[1]
                    pid = parts[4].strip()
                    if pid == current_pid: continue
                    for port in ports:
                        if local_address.endswith(f":{port}"):
                            pids_to_kill.add(pid)
            
            if pids_to_kill:
                print(f"   [C] Eliminando {len(pids_to_kill)} proceso(s)...")
                pid_args = " ".join([f"/pid {pid}" for pid in pids_to_kill])
                subprocess.run(f"taskkill /f {pid_args}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                print(f"   [D] Limpieza completada.")
            else:
                print(f"   [D] No se requiere limpieza.")
        except subprocess.TimeoutExpired:
            if sys.platform == "win32":
                result = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
                for line in result.splitlines():
                    parts = line.split()
                    if len(parts) > 4 and f":{port}" in parts[1]:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

def main():
    print("==================================================")
    print("Iniciando Sistema de Gestión DIF Acatlán (FORMADIG)")
    print("==================================================")

    # Limpiar puertos clave para evitar conflictos
    ports = [5001, 5004, 5005, 5006, 5007, 8000]
    print(f"Limpiando puertos ({', '.join(map(str, ports))})...")
    kill_ports(ports)

    base_dir  = os.path.dirname(os.path.abspath(__file__))
    system_dir = os.path.join(base_dir, "Formadig", "1_Sistema_DIF_Acatlan")
    modulos_dir = os.path.join(system_dir, "modulos")
    
    backends = {
        "Auth": os.path.join(modulos_dir, "login", "logica", "login_backend.py"),
        "Traslados": os.path.join(modulos_dir, "admin_traslados", "logica", "admin_traslados_backend.py"),
        "Desayunos Fríos": os.path.join(modulos_dir, "admin_desayunos_frios", "logica", "admin_desayunos_frios_backend.py"),
        "Desayunos Calientes": os.path.join(modulos_dir, "admin_desayunos_calientes", "logica", "admin_desayunos_calientes_backend.py"),
        "EAEyD": os.path.join(modulos_dir, "admin_espacios_eaeyd", "logica", "admin_espacios_eaeyd_backend.py"),
        "Chatbot": os.path.join(modulos_dir, "chatbot", "logica", "chatbot_backend.py"),
        "SMS": os.path.join(modulos_dir, "sms", "logica", "sms_backend.py")
    }

    procesos = []

    for name, path in backends.items():
        if os.path.exists(path):
            print(f"Iniciando {name} Backend...")
            procesos.append(subprocess.Popen([sys.executable, path]))
        else:
            print(f"⚠️ Error: No se encontró el módulo {name} en {path}")

    print("Iniciando Servidor Web (Puerto 8000)...")
    procesos.append(subprocess.Popen([sys.executable, "-m", "http.server", "8000"], cwd=system_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    time.sleep(3)
    url = "http://localhost:8000/modulos/login/vistas/login.html"
    print(f"\n🚀 SITEMA LISTO: {url}")
    print("Presiona Ctrl+C para apagar.")
    
    webbrowser.open(url)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nApagando servidores...")
        for p in procesos: p.terminate()
        print("¡Adiós!")

if __name__ == "__main__":
    main()