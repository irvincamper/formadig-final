import os
import sys
import subprocess

def iniciar_sistema():
    """Script puente para iniciar el sistema desde la nueva estructura organizada."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Ruta al nuevo script de control
    script_control = os.path.join(base_dir, "0_Inicio_Rapido", "servidor_control.py")
    
    if os.path.exists(script_control):
        print(f"Redirigiendo inicio a: {script_control}")
        try:
            # Ejecutamos el script de control en su propio directorio
            subprocess.run([sys.executable, script_control], cwd=os.path.dirname(script_control))
        except KeyboardInterrupt:
            print("\nSistema detenido por el usuario.")
    else:
        print(f"Error crítico: No se encuentra el controlador en {script_control}")
        print("Asegúrate de estar en la carpeta raíz 'Formadig'.")

if __name__ == "__main__":
    iniciar_sistema()
