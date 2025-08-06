-- =====================================================
-- PROCEDIMIENTO PARA GESTIONAR RESERVAS (VERSIÓN SIMPLIFICADA)
-- =====================================================

-- Eliminar el procedimiento anterior si existe
DROP PROCEDURE IF EXISTS public.proc_gestionar_reserva(
    character varying, integer, integer, integer, date, 
    time without time zone, time without time zone, text, character varying
);

-- Procedimiento simplificado para gestionar reservas
CREATE OR REPLACE PROCEDURE public.proc_gestionar_reserva(
    IN p_accion character varying,
    IN p_id integer DEFAULT NULL,
    IN p_cliente_id integer DEFAULT NULL,
    IN p_cancha_id integer DEFAULT NULL,
    IN p_fecha_reserva date DEFAULT NULL,
    IN p_hora_inicio time without time zone DEFAULT NULL,
    IN p_hora_fin time without time zone DEFAULT NULL,
    IN p_observaciones text DEFAULT NULL,
    IN p_estado character varying DEFAULT 'pendiente'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_reserva_id INTEGER;
    v_duracion DECIMAL(10,2);
    v_disponible BOOLEAN;
BEGIN
    -- Validar parámetros de entrada
    IF p_accion IS NULL OR p_accion NOT IN ('CREATE', 'UPDATE', 'CANCEL') THEN
        RAISE EXCEPTION 'Acción no válida. Debe ser CREATE, UPDATE o CANCEL';
    END IF;
    
    CASE p_accion
        WHEN 'CREATE' THEN
            -- Calcular duración
            v_duracion := EXTRACT(EPOCH FROM (p_hora_fin - p_hora_inicio)) / 3600;
            
            -- Validar duración
            IF v_duracion <= 0 THEN
                RAISE EXCEPTION 'La duración debe ser mayor a 0 horas';
            END IF;
            
            -- Validar fecha
            IF p_fecha_reserva < CURRENT_DATE THEN
                RAISE EXCEPTION 'No se pueden crear reservas en fechas pasadas';
            END IF;
            
            -- Verificar disponibilidad
            SELECT verificar_disponibilidad_cancha(p_cancha_id, p_fecha_reserva, p_hora_inicio, p_hora_fin) 
            INTO v_disponible;
            
            IF NOT v_disponible THEN
                RAISE EXCEPTION 'La cancha no está disponible en el horario especificado';
            END IF;
            
            -- Crear la reserva
            INSERT INTO reservas (
                cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin,
                duracion, observaciones, estado, fecha_creacion, fecha_actualizacion
            ) VALUES (
                p_cliente_id, p_cancha_id, p_fecha_reserva, p_hora_inicio, p_hora_fin,
                v_duracion, p_observaciones, p_estado, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) RETURNING id INTO v_reserva_id;
            
            RAISE NOTICE 'Reserva creada exitosamente con ID: %', v_reserva_id;
            
        WHEN 'UPDATE' THEN
            -- Calcular duración
            v_duracion := EXTRACT(EPOCH FROM (p_hora_fin - p_hora_inicio)) / 3600;
            
            -- Validar duración
            IF v_duracion <= 0 THEN
                RAISE EXCEPTION 'La duración debe ser mayor a 0 horas';
            END IF;
            
            -- Validar fecha
            IF p_fecha_reserva < CURRENT_DATE THEN
                RAISE EXCEPTION 'No se pueden crear reservas en fechas pasadas';
            END IF;
            
            -- Verificar disponibilidad (excluyendo la reserva actual)
            SELECT NOT EXISTS (
                SELECT 1 FROM reservas 
                WHERE cancha_id = p_cancha_id 
                AND fecha_reserva = p_fecha_reserva
                AND id != p_id
                AND estado IN ('confirmada', 'pendiente')
                AND (
                    (hora_inicio < p_hora_fin AND hora_fin > p_hora_inicio) OR
                    (hora_inicio >= p_hora_inicio AND hora_inicio < p_hora_fin)
                )
            ) INTO v_disponible;
            
            IF NOT v_disponible THEN
                RAISE EXCEPTION 'La cancha no está disponible en el horario especificado';
            END IF;
            
            -- Actualizar la reserva
            UPDATE reservas SET
                cliente_id = p_cliente_id,
                cancha_id = p_cancha_id,
                fecha_reserva = p_fecha_reserva,
                hora_inicio = p_hora_inicio,
                hora_fin = p_hora_fin,
                duracion = v_duracion,
                observaciones = p_observaciones,
                estado = p_estado,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = p_id;
            
            RAISE NOTICE 'Reserva actualizada exitosamente';
            
        WHEN 'CANCEL' THEN
            -- Cancelar la reserva
            UPDATE reservas SET
                estado = 'cancelada',
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = p_id;
            
            RAISE NOTICE 'Reserva cancelada exitosamente';
    END CASE;
END;
$$;

-- Otorgar permisos al procedimiento
GRANT EXECUTE ON PROCEDURE public.proc_gestionar_reserva(
    character varying, integer, integer, integer, date, 
    time without time zone, time without time zone, text, character varying
) TO admin_reservas;

GRANT EXECUTE ON PROCEDURE public.proc_gestionar_reserva(
    character varying, integer, integer, integer, date, 
    time without time zone, time without time zone, text, character varying
) TO operador_reservas; 