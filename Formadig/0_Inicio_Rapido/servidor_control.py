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
    print("Arquitectura Unificada - Un Puerto, Una Instancia")
    print("==================================================")

    # Limpiar puertos antiguos (por si quedan procesos de versión anterior)
    old_ports = [5001, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010]
    print(f"Limpiando puertos antiguos ({', '.join(map(str, old_ports))})...")
    kill_ports(old_ports)
    
    # Limpiar puerto del nuevo servidor unificado
    print(f"Limpiando puerto 8000 del servidor unificado...")
    kill_ports([8000])

    base_dir  = os.path.dirname(os.path.abspath(__file__))
    root_dir  = os.path.dirname(base_dir)
    system_dir = os.path.join(root_dir, "1_Sistema_DIF_Acatlan")
    app_unified = os.path.join(system_dir, "app_unified.py")
    
    if not os.path.exists(app_unified):
        print(f"❌ Error: No se encontró {app_unified}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🚀 Iniciando APLICACIÓN MAESTRA UNIFICADA...")
    print("="*70 + "\n")
    
    # Iniciar la aplicación maestra unificada
    print(f"▶️ Ejecutando: python {app_unified}\n")
    
    try:
        # Ejecutar la app en el directorio correcto para que encuentre los módulos
        proceso = subprocess.Popen(
            [sys.executable, app_unified],
            cwd=system_dir,
            env={**os.environ, 'PORT': '8000'}
        )
        
        # Esperar a que el servidor esté listo
        time.sleep(4)
        
        url = "http://localhost:8000/modulos/login/vistas/login.html"
        print(f"\n✅ SISTEMA LISTO EN: {url}")
        print("\n📋 Arquictectura:")
        print("   - 1 Aplicación Flask Maestra")
        print("   - 9 Blueprints registrados")
        print("   - 1 Puerto único (8000)")
        print("   - CORS habilitado globalmente")
        print("\nPresiona Ctrl+C para apagar.")
        
        webbrowser.open(url)
        
        # Mantener el proceso activo
        proceso.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Apagando aplicación...")
        proceso.terminate()
        proceso.wait(timeout=5)
        print("✅ Aplicación cerrada.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
