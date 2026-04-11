import os
import subprocess
import sys
import webbrowser
import time

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
    print("Iniciando Sistema de Gestión DIF Acatlán (FORMADIG v2.1)")
    print("==================================================")

    # Limpiar puertos clave para evitar conflictos (5003 para Admin Usuarios, 5009 para SMS, 5010 para Colonias)
    ports = [5001, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 8000]
    print(f"Limpiando puertos ({', '.join(map(str, ports))})...")
    kill_ports(ports)

    base_dir  = os.path.dirname(os.path.abspath(__file__))
    # El archivo está en 0_Inicio_Rapido, subimos un nivel para encontrar el resto
    root_dir  = os.path.dirname(base_dir)
    system_dir = os.path.join(root_dir, "1_Sistema_DIF_Acatlan")
    modulos_dir = os.path.join(system_dir, "modulos")
    
    backends = {
        "Auth": os.path.join(modulos_dir, "login", "logica", "login_backend.py"),
        "Admin Usuarios": os.path.join(modulos_dir, "admin_usuarios", "logica", "admin_usuarios_backend.py"),
        "Traslados": os.path.join(modulos_dir, "admin_traslados", "logica", "admin_traslados_backend.py"),
        "Desayunos Fríos": os.path.join(modulos_dir, "admin_desayunos_frios", "logica", "admin_desayunos_frios_backend.py"),
        "Desayunos Calientes": os.path.join(modulos_dir, "admin_desayunos_calientes", "logica", "admin_desayunos_calientes_backend.py"),
        "EAEyD": os.path.join(modulos_dir, "admin_espacios_eaeyd", "logica", "admin_espacios_eaeyd_backend.py"),
        "Chatbot": os.path.join(modulos_dir, "chatbot", "logica", "chatbot_backend.py"),
        "SMS": os.path.join(modulos_dir, "sms", "logica", "sms_backend.py"),
        "Colonias": os.path.join(modulos_dir, "colonias", "logica", "colonias_backend.py")
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
