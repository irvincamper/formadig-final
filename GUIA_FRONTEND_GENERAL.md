# Próximo frontend general de FORMADIG

La base remota main ya contiene el diseño clínico 405ea50. La corrección local de login aún no está publicada: consultar INFORME_INTEGRACION_MAIN_RENDER.md antes de integrar.

Conservar primero el trabajo local mediante commit en su rama. No ejecutar reset --hard ni borrar archivos. Después:

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feat/frontend-general
```

Si el pull no puede avanzar por fast-forward, detenerse e inspeccionar las divergencias. Si la rama de frontend ya existe, continuar en ella sin sobrescribirla.

Modificar progresivamente HTML y CSS bajo Formadig/1_Sistema_DIF_Acatlan, incluidos dashboard.html, css y los directorios modulos/*/vistas y modulos/*/diseno. Evitar las copias históricas dif_acatlan_system y 2_Interfaz_Web_Moderna: run.py sirve 1_Sistema_DIF_Acatlan.

Conservar los IDs y name de campos, formularios, tipos de botones, href, scripts y atributos usados por JavaScript. Respetar CONTRATO_FRONTEND.md. Cambios en core/*.js o modulos/*/logica/*.js requieren revisar eventos, endpoints, métodos HTTP, payloads, respuestas, sesión y permisos. No cambiar backend Python, .env, roles, Supabase/RLS, móvil ni banderas clínicas como parte de una tarea visual.

Validar cada módulo con teclado, errores, formularios, navegación y tamaño estrecho. Ejecutar las suites Python y Node y las demos Playwright descritas en INFORME_VALIDACION_VISUAL.md; sus datos son sintéticos y no prueban producción.

```powershell
git diff --check
git status --short
git add <archivos-revisados>
git commit -m "style: mejora interfaz general de FORMADIG"
git push -u origin feat/frontend-general
```

Crear un Pull Request en GitHub con base main y compare feat/frontend-general. Incluir capturas, módulos modificados, pruebas y limitaciones. Solicitar revisión funcional antes de fusionar: no hacer push directo a main.

Después de aprobar y fusionar, comprobar en Render que el despliegue desde main finaliza Live y que su SHA coincide con el commit fusionado. Revisar /health, /api/status, login con cuenta autorizada, navegación y módulos cambiados. Si falla, revisar logs y comunicar el estado; no aplicar restauraciones destructivas ni habilitar escrituras clínicas para resolver una prueba.
