CREATE OR REPLACE FUNCTION public.crear_notificacion_por_cambio_estatus()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

DECLARE

    tipo_apoyo TEXT;

BEGIN

    -- Detectar quÃ© tabla disparÃ³ el trigger

    tipo_apoyo := CASE

        WHEN TG_TABLE_NAME = 'desayunos_frios' THEN 'Desayuno FrÃ­o'

        WHEN TG_TABLE_NAME = 'desayunos_calientes' THEN 'Desayuno Caliente'

        WHEN TG_TABLE_NAME = 'desayunos_eaeyd' THEN 'EAEyD'

        WHEN TG_TABLE_NAME = 'traslados' THEN 'Traslado MÃ©dico'

        ELSE 'Apoyo'

    END;



    -- Solo insertar si el estatus realmente cambiÃ³

    IF (OLD.estatus IS DISTINCT FROM NEW.estatus) THEN

        INSERT INTO public.notificaciones (usuario_id, titulo, mensaje)

        VALUES (

            NEW.registrado_por,

            'ActualizaciÃ³n de Solicitud',

            'Tu solicitud de ' || tipo_apoyo || ' ha cambiado a: ' || NEW.estatus

        );

    END IF;

    RETURN NEW;

END;

$function$
;
