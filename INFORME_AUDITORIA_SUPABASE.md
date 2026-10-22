# FORMADIG: auditoría de Supabase

Fecha: 21 de octubre de 2026. Proyecto verificado en el navegador: `DIF`, referencia `ctiqbycbkcftwuqgzxjb`, rama Supabase `main PRODUCTION`. Rama Git: `feat/psicologia-dentista`.

## Conexión y alcance

Servidor de Codex configurado en el archivo de usuario `C:\Users\Herna\.codex\config.toml` como `supabase_formadig_readonly`.

URL: `https://mcp.supabase.com/mcp?project_ref=ctiqbycbkcftwuqgzxjb&read_only=true&features=database,docs`.

Lista de herramientas permitidas: `list_tables`, `execute_sql`, `search_docs`. OAuth completado y confirmado por Codex en esta conversación. El servidor personalizado todavía no está expuesto como herramienta en esta sesión. El conector del plugin Supabase devolvió `You do not have permission to perform this action`; por ello, la auditoría se realizó en el navegador interno autenticado, mediante SELECT a `information_schema` y `pg_catalog`. El SQL Editor utiliza permisos de la sesión del panel: no hereda la restricción técnica de solo lectura del MCP. Todas las consultas ejecutadas fueron exclusivamente de metadatos.

No se consultaron filas de pacientes, perfiles ni atenciones. No se modificaron esquema, registros, políticas, código funcional ni Render. No se almacenaron credenciales en el repositorio. Se desactivó el autoguardado del SQL Editor; el panel mostró un borrador de consulta sin guardar.

## Tablas y columnas

### public.modulo_dental

| Columna | Tipo | Admite NULL | Valor predeterminado |
|---|---|---|---|
| id | uuid | No | gen_random_uuid() |
| paciente_id | uuid | No | Sin valor |
| atendido_por | uuid | Sí | Sin valor |
| motivo_consulta | text | No | Sin valor |
| diagnostico | text | Sí | Sin valor |
| tratamiento_realizado | text | Sí | Sin valor |
| costo_recuperacion | numeric(10,2) | Sí | 0.00 |
| fecha_atencion | timestamp with time zone | Sí | now() |

### public.modulo_psicologia

| Columna | Tipo | Admite NULL | Valor predeterminado |
|---|---|---|---|
| id | uuid | No | gen_random_uuid() |
| paciente_id | uuid | No | Sin valor |
| atendido_por | uuid | Sí | Sin valor |
| tipo_atencion | text | No | Sin valor |
| motivo_consulta | text | No | Sin valor |
| diagnostico_inicial | text | Sí | Sin valor |
| numero_sesion | integer | Sí | 1 |
| estatus_caso | text | Sí | 'En proceso'::text |
| fecha_sesion | timestamp with time zone | Sí | now() |

## Relaciones y restricciones

Ambas tablas tienen `PRIMARY KEY (id)`, con nombres `modulo_dental_pkey` y `modulo_psicologia_pkey`.

En ambas tablas:

- `paciente_id` referencia `public.perfiles(id)` con `ON DELETE CASCADE`.
- `atendido_por` referencia `public.perfiles(id)` con `ON DELETE SET NULL`.
- Las claves foráneas se llaman `<tabla>_paciente_id_fkey` y `<tabla>_atendido_por_fkey`.
- No se encontraron otras restricciones CHECK/UNIQUE ni claves foráneas entrantes hacia estas tablas en `pg_constraint`.
- Sólo existe el índice B-tree único de la clave primaria; no hay índices adicionales sobre paciente o profesional.
- No hay triggers propios de usuario. Los triggers internos de integridad referencial se excluyeron de esta comprobación.

Implicaciones del esquema actual: no se exige costo no negativo, número de sesión positivo, catálogo de tipos/estatus ni que paciente y profesional sean distintos. Los campos NOT NULL de texto pueden contener una cadena vacía si el backend no la rechaza. Los valores predeterminados no impiden insertar NULL explícito donde la columna lo admite.

## RLS y privilegios

Ambas tablas tienen `relrowsecurity=true` y `relforcerowsecurity=false`.

| Tabla | Política | Operación | Roles | Condición |
|---|---|---|---|---|
| modulo_dental | Lectura publica modulo_dental | SELECT | PUBLIC | USING (true) |
| modulo_dental | Insercion modulo_dental | INSERT | PUBLIC | WITH CHECK (true) |
| modulo_psicologia | Lectura publica modulo_psicologia | SELECT | PUBLIC | USING (true) |
| modulo_psicologia | Insercion modulo_psicologia | INSERT | PUBLIC | WITH CHECK (true) |

Todas son PERMISSIVE. No se encontraron políticas UPDATE o DELETE en estas tablas.

En ambas tablas, los roles `anon`, `authenticated` y `service_role` tienen concedidos SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES y TRIGGER, según `information_schema.table_privileges`.

Hallazgo prioritario: las políticas SELECT e INSERT no aplican aislamiento por usuario, paciente o profesional. PUBLIC incluye los roles de acceso habituales. La posibilidad de acceso externo también depende de la exposición de la tabla por Data API y de permisos de esquema; no se comprobó leyendo registros ni haciendo inserciones. RLS no protege TRUNCATE y los privilegios SQL observados son más amplios que los requeridos por una interfaz clínica. La ausencia de políticas UPDATE/DELETE bloquea esas operaciones para roles sujetos a RLS, aunque tengan GRANT; el propietario y roles con bypass requieren evaluación separada. No se cambiaron permisos.

## Dependencias con FORMADIG

`public.perfiles` es la dependencia compartida. Sus columnas observadas son: `id uuid NOT NULL`, `nombre_usuario text`, `nombre_completo text`, `rol text`, `fecha_creacion timestamptz`, `curp text`, `telefono text`, `domicilio text`, `apellidos text` y `clave_elector text`; todas salvo id admiten NULL.

Sus restricciones son `PRIMARY KEY(id)`, `UNIQUE(nombre_usuario)` y `FOREIGN KEY(id) REFERENCES auth.users(id) ON DELETE CASCADE`. Por tanto, el paciente y el profesional deben disponer de perfil ligado a un usuario de Supabase Auth bajo el modelo actual. La eliminación de ese usuario puede propagarse al perfil y a sus atenciones como paciente; este efecto se desprende de las claves foráneas, sin probar eliminaciones.

Otras tablas con FK a perfiles son `traslados.registrado_por` y `chatbot_historial.usuario_id`. No se encontró relación FK directa entre esas tablas y los dos módulos clínicos.

En el código local, `run.py` no registra blueprints para Psicología o Dental. La administración de usuarios permite actualmente sólo `admin`, `admin_desayunos` y `admin_traslados`, tanto en su backend como en JavaScript. Habrá que definir posteriormente el modelo de roles y autorización para los profesionales. No se modificó ese código.

## Pendientes antes de implementar

1. Cargar y probar el servidor MCP personalizado en una sesión que lo exponga, o resolver la autorización del conector del plugin. OAuth completado no equivale a una consulta MCP exitosa.
2. Definir permisos de pacientes, profesionales y administradores antes de diseñar políticas clínicas.
3. Decidir si todo paciente debe tener cuenta Auth, conforme a la FK existente.
4. Revisar el borrado en cascada, las validaciones de negocio, los índices de consulta y la exposición Data API cuando se autorice implementación.

La auditoría del esquema se completó mediante el panel autenticado; la verificación de una llamada mediante el servidor MCP personalizado sigue pendiente. No se ejecutaron commits, push ni acciones sobre Render.
