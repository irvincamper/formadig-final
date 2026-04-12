-- ============================================================================
-- SCRIPT SQL PARA SUPABASE - CONFIGURAR TABLA DESAYUNOS_CALIENTES
-- Ejecutar en: SQL Editor del Dashboard de Supabase
-- ============================================================================

-- OPCIÓN 1: DESHABILITAR RLS COMPLETAMENTE (Más Rápido - Recomendado para desarrollo)
-- ===================================================================================
-- Si tu API aún tiene restricciones RLS bloqueando lecturas, ejecuta esto:

ALTER TABLE public.desayunos_calientes DISABLE ROW LEVEL SECURITY;

-- Esto permitirá que tu API lea y escriba sin restricciones RLS.


-- OPCIÓN 2: CREAR POLÍTICAS RLS PERMISIVAS (Si prefieres mantener RLS activo)
-- ===========================================================================
-- Desactiva RLS primero si está activa:
-- ALTER TABLE public.desayunos_calientes DISABLE ROW LEVEL SECURITY;

-- Luego, si quieres volver a habilitarla después con políticas permisivas:
-- ALTER TABLE public.desayunos_calientes ENABLE ROW LEVEL SECURITY;

-- Crear política SELECT (Lectura permitida para todos)
CREATE POLICY "Enable SELECT for all"
ON public.desayunos_calientes
FOR SELECT
USING (TRUE);

-- Crear política INSERT (Inserción permitida para todos)
CREATE POLICY "Enable INSERT for all"
ON public.desayunos_calientes
FOR INSERT
WITH CHECK (TRUE);

-- Crear política UPDATE (Actualización permitida para todos)
CREATE POLICY "Enable UPDATE for all"
ON public.desayunos_calientes
FOR UPDATE
USING (TRUE)
WITH CHECK (TRUE);

-- Crear política DELETE (Eliminación permitida para todos)
CREATE POLICY "Enable DELETE for all"
ON public.desayunos_calientes
FOR DELETE
USING (TRUE);


-- OPCIÓN 3: VERIFICAR COLUMNAS DE LA TABLA (Diagnóstico)
-- =======================================================
-- Ejecuta esto para verificar que la tabla exista y tenga las columnas correctas:

SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM 
    information_schema.columns 
WHERE 
    table_name = 'desayunos_calientes' 
ORDER BY 
    ordinal_position;

-- Resultado esperado: Debe mostrar columnas como:
-- id, nombres, apellidos, curp, fecha_nacimiento, sexo, estado_civil,
-- peso_menor, estatura_menor, nivel_estudios, ingreso_mensual,
-- situacion_vulnerabilidad, localidad, tipo_asentamiento, cp, referencias,
-- tutor_nombre, telefono, url_curp, url_comprobante_salud, url_ine_tutor,
-- url_comprobante_domicilio, url_foto_infante, escuela, estatus, etc.


-- OPCIÓN 4: VERIFICAR ESTADO RLS (Diagnóstico)
-- ============================================
-- Ejecuta esto para ver el estado actual de RLS:

SELECT 
    schemaname, 
    tablename, 
    rowsecurity 
FROM 
    pg_tables 
WHERE 
    tablename = 'desayunos_calientes';

-- Resultado esperado:
-- schemaname | tablename              | rowsecurity
-- public     | desayunos_calientes    | f (FALSE = RLS deshabilitado) ✅
-- public     | desayunos_calientes    | t (TRUE = RLS habilitado)  ⚠️


-- OPCIÓN 5: CREAR LA TABLA DESDE CERO (Si no existe)
-- ==================================================
-- Ejecuta esto solo si la tabla desayunos_calientes NO existe:

CREATE TABLE IF NOT EXISTS public.desayunos_calientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombres TEXT,
    apellidos TEXT,
    curp TEXT,
    fecha_nacimiento DATE,
    sexo TEXT,
    estado_civil TEXT,
    peso_menor NUMERIC,
    estatura_menor NUMERIC,
    nivel_estudios TEXT,
    ingreso_mensual NUMERIC,
    situacion_vulnerabilidad BOOLEAN DEFAULT FALSE,
    localidad TEXT,
    tipo_asentamiento TEXT,
    cp TEXT,
    referencias TEXT,
    tutor_nombre TEXT,
    telefono TEXT,
    url_curp TEXT,
    url_comprobante_salud TEXT,
    url_ine_tutor TEXT,
    url_comprobante_domicilio TEXT,
    url_foto_infante TEXT,
    escuela TEXT DEFAULT 'No asignada',
    estatus TEXT DEFAULT 'APROBADO',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    usuario_admin UUID
);

-- Grantear permisos a anon y authenticated
GRANT ALL PRIVILEGES ON TABLE public.desayunos_calientes TO anon, authenticated;


-- ============================================================================
-- PRÓXIMOS PASOS
-- ============================================================================
-- 1. Copia el script SQL relevante (Opción 1 es la recomendada)
-- 2. Ve a tu dashboard de Supabase → SQL Editor
-- 3. Pega el script y ejecuta (Run query)
-- 4. Verás: "Query executed successfully!" ✅
-- 5. Vuelve a cargar el módulo de Desayunos Calientes en tu app
-- 6. Debería dejar de mostrar "Cargando registros..." y cargar los datos ✅

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================
-- Si aún no funciona después de ejecutar el script:
--
-- A) Verifica que la tabla 'desayunos_calientes' exista:
--    - Ve a Supabase Dashboard → Tables → busca 'desayunos_calientes'
--    - Si NO existe, ejecuta la OPCIÓN 5 (crear tabla)
--
-- B) Verifica que haya datos en la tabla:
--    - SQL Editor: SELECT COUNT(*) FROM desayunos_calientes;
--    - Si devuelve 0, agreg datos de prueba manualmente
--
-- C) Verifica el estado del RLS:
--    - Ejecuta la OPCIÓN 4 para ver rowsecurity
--    - Si es TRUE, ejecuta Opción 1 para deshabilitarlo
--
-- D) Revisa la consola del navegador:
--    - F12 → Console → busca mensajes de error
--    - Asegúrate de que la respuesta sea JSON válido
--
-- E) Verifica los logs del backend:
--    - Busca mensajes tipo: "❌ ErrorAl obtener registros: ..."
--
-- Si persiste el problema, contacta al equipo de desarrollo.
