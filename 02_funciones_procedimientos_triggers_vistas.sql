-- =====================================================
-- FUNCIONES, PROCEDIMIENTOS, TRIGGERS Y VISTAS
-- =====================================================
-- Archivo: 02_funciones_procedimientos_triggers_vistas.sql
-- Descripción: Contiene todas las funciones, procedimientos, triggers y vistas
-- Fecha: 2025-08-03
-- =====================================================

-- =====================================================
-- FUNCIONES ALMACENADAS
-- =====================================================

-- Función para actualizar cancha
CREATE FUNCTION public.actualizar_cancha(p_id integer, p_nombre character varying, p_tipo_deporte character varying, p_capacidad integer, p_precio_hora numeric, p_estado character varying, p_horario_apertura time without time zone, p_horario_cierre time without time zone, p_descripcion text, p_tipo_cancha_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE canchas 
    SET nombre = p_nombre,
        tipo_deporte = p_tipo_deporte,
        capacidad = p_capacidad,
        precio_hora = p_precio_hora,
        estado = p_estado,
        horario_apertura = p_horario_apertura,
        horario_cierre = p_horario_cierre,
        descripcion = p_descripcion,
        tipo_cancha_id = p_tipo_cancha_id,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = p_id;
    
    RETURN FOUND;
END;
$$;
ALTER FUNCTION public.actualizar_cancha(p_id integer, p_nombre character varying, p_tipo_deporte character varying, p_capacidad integer, p_precio_hora numeric, p_estado character varying, p_horario_apertura time without time zone, p_horario_cierre time without time zone, p_descripcion text, p_tipo_cancha_id integer) OWNER TO postgres;

-- Función para actualizar fecha de tipos de cancha
CREATE FUNCTION public.actualizar_fecha_tipos_cancha() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.actualizar_fecha_tipos_cancha() OWNER TO postgres;

-- Función para crear cancha
CREATE FUNCTION public.crear_cancha(p_nombre character varying, p_tipo_deporte character varying, p_capacidad integer, p_precio_hora numeric, p_estado character varying, p_horario_apertura time without time zone, p_horario_cierre time without time zone, p_descripcion text, p_tipo_cancha_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    nuevo_id INTEGER;
BEGIN
    INSERT INTO canchas (
        nombre, tipo_deporte, capacidad, precio_hora, estado,
        horario_apertura, horario_cierre, descripcion, tipo_cancha_id
    )
    VALUES (
        p_nombre, p_tipo_deporte, p_capacidad, p_precio_hora, p_estado,
        p_horario_apertura, p_horario_cierre, p_descripcion, p_tipo_cancha_id
    )
    RETURNING id INTO nuevo_id;
    
    RETURN nuevo_id;
END;
$$;
ALTER FUNCTION public.crear_cancha(p_nombre character varying, p_tipo_deporte character varying, p_capacidad integer, p_precio_hora numeric, p_estado character varying, p_horario_apertura time without time zone, p_horario_cierre time without time zone, p_descripcion text, p_tipo_cancha_id integer) OWNER TO postgres;

-- Función para crear reserva
CREATE FUNCTION public.crear_reserva(p_cliente_id integer, p_cancha_id integer, p_fecha_reserva date, p_hora_inicio time without time zone, p_hora_fin time without time zone, p_observaciones text DEFAULT NULL::text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_reserva_id INTEGER;
    v_duracion DECIMAL(10,2);
BEGIN
    -- Calcular la duración en horas
    v_duracion := EXTRACT(EPOCH FROM (p_hora_fin - p_hora_inicio)) / 3600;
    
    -- Insertar la reserva incluyendo la duración calculada
    INSERT INTO reservas (
        cliente_id,
        cancha_id,
        fecha_reserva,
        hora_inicio,
        hora_fin,
        duracion,
        observaciones,
        estado
    ) VALUES (
        p_cliente_id,
        p_cancha_id,
        p_fecha_reserva,
        p_hora_inicio,
        p_hora_fin,
        v_duracion,
        p_observaciones,
        'pendiente'
    ) RETURNING id INTO v_reserva_id;
    
    RETURN v_reserva_id;
END;
$$;
ALTER FUNCTION public.crear_reserva(p_cliente_id integer, p_cancha_id integer, p_fecha_reserva date, p_hora_inicio time without time zone, p_hora_fin time without time zone, p_observaciones text) OWNER TO postgres;

-- Función para crear tipo de cancha
CREATE FUNCTION public.crear_tipo_cancha(p_nombre character varying, p_descripcion text, p_precio_por_hora numeric) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    nuevo_id INTEGER;
BEGIN
    INSERT INTO tipos_cancha (nombre, descripcion, precio_por_hora)
    VALUES (p_nombre, p_descripcion, p_precio_por_hora)
    RETURNING id INTO nuevo_id;
    
    RETURN nuevo_id;
END;
$$;
ALTER FUNCTION public.crear_tipo_cancha(p_nombre character varying, p_descripcion text, p_precio_por_hora numeric) OWNER TO postgres;

-- Función para eliminar cancha
CREATE FUNCTION public.eliminar_cancha(p_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM canchas WHERE id = p_id;
    RETURN FOUND;
END;
$$;
ALTER FUNCTION public.eliminar_cancha(p_id integer) OWNER TO postgres;

-- Función para obtener cancha por ID
CREATE FUNCTION public.obtener_cancha_por_id(p_id integer) RETURNS TABLE(id integer, nombre character varying, tipo_deporte character varying, capacidad integer, precio_hora numeric, estado character varying, horario_apertura time without time zone, horario_cierre time without time zone, descripcion text, fecha_creacion timestamp without time zone, fecha_actualizacion timestamp without time zone, tipo_cancha_id integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora,
           c.estado, c.horario_apertura, c.horario_cierre, c.descripcion,
           c.fecha_creacion, c.fecha_actualizacion, c.tipo_cancha_id
    FROM canchas c
    WHERE c.id = p_id;
END;
$$;
ALTER FUNCTION public.obtener_cancha_por_id(p_id integer) OWNER TO postgres;

-- Función para obtener canchas
CREATE FUNCTION public.obtener_canchas() RETURNS TABLE(id integer, nombre character varying, tipo_deporte character varying, capacidad integer, precio_hora numeric, estado character varying, horario_apertura time without time zone, horario_cierre time without time zone, descripcion text, fecha_creacion timestamp without time zone, fecha_actualizacion timestamp without time zone, tipo_cancha_id integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora,
           c.estado, c.horario_apertura, c.horario_cierre, c.descripcion,
           c.fecha_creacion, c.fecha_actualizacion, c.tipo_cancha_id
    FROM canchas c
    ORDER BY c.nombre;
END;
$$;
ALTER FUNCTION public.obtener_canchas() OWNER TO postgres;

-- Función para obtener canchas con tipos
CREATE FUNCTION public.obtener_canchas_con_tipos() RETURNS TABLE(id integer, nombre_cancha character varying, descripcion_cancha text, capacidad integer, precio_hora numeric, estado character varying, tipo_cancha_nombre character varying, tipo_cancha_descripcion text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.nombre as nombre_cancha,
        c.descripcion as descripcion_cancha,
        c.capacidad,
        c.precio_hora,
        c.estado,
        c.tipo_deporte as tipo_cancha_nombre,
        c.descripcion as tipo_cancha_descripcion
    FROM canchas c
    ORDER BY c.nombre;
END;
$$;
ALTER FUNCTION public.obtener_canchas_con_tipos() OWNER TO postgres;

-- Función para obtener tipos de cancha
CREATE FUNCTION public.obtener_tipos_cancha() RETURNS TABLE(id integer, nombre character varying, descripcion text, precio_por_hora numeric, estado character varying, fecha_creacion timestamp without time zone, fecha_actualizacion timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT tc.id, tc.nombre, tc.descripcion, tc.precio_por_hora, 
           tc.estado, tc.fecha_creacion, tc.fecha_actualizacion
    FROM tipos_cancha tc
    ORDER BY tc.nombre;
END;
$$;
ALTER FUNCTION public.obtener_tipos_cancha() OWNER TO postgres;

-- Función para registrar auditoría automática
CREATE FUNCTION public.registrar_auditoria_automatica() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_usuario_id INTEGER;
    v_tipo_accion VARCHAR(20);
    v_tabla_nombre VARCHAR(50);
    v_registro_id INTEGER;
    v_detalles TEXT;
BEGIN
    -- Obtener el usuario actual (asumiendo que está en una variable de sesión)
    -- Por ahora usaremos NULL, pero puedes configurar esto según tu sistema
    v_usuario_id := NULL;
    
    -- Determinar el tipo de acción
    IF TG_OP = 'INSERT' THEN
        v_tipo_accion := 'INSERT';
        v_registro_id := NEW.id;
        v_detalles := 'Nuevo registro creado';
    ELSIF TG_OP = 'UPDATE' THEN
        v_tipo_accion := 'UPDATE';
        v_registro_id := NEW.id;
        v_detalles := 'Registro actualizado';
    ELSIF TG_OP = 'DELETE' THEN
        v_tipo_accion := 'DELETE';
        v_registro_id := OLD.id;
        v_detalles := 'Registro eliminado';
    END IF;
    
    -- Obtener el nombre de la tabla
    v_tabla_nombre := TG_TABLE_NAME;
    
    -- Insertar en la tabla auditoría
    INSERT INTO auditoria (
        usuario_id,
        tipo_accion,
        tabla,
        registro_id,
        detalles,
        resultado,
        ip_address,
        fecha_hora
    ) VALUES (
        v_usuario_id,
        v_tipo_accion,
        v_tabla_nombre,
        v_registro_id,
        v_detalles,
        'SUCCESS',
        '127.0.0.1',
        CURRENT_TIMESTAMP
    );
    
    -- Retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;
ALTER FUNCTION public.registrar_auditoria_automatica() OWNER TO postgres;

-- Función para actualizar columna updated_at
CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

-- Función para verificar disponibilidad de cancha
CREATE FUNCTION public.verificar_disponibilidad_cancha(p_cancha_id integer, p_fecha date, p_hora_inicio time without time zone, p_hora_fin time without time zone) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN NOT EXISTS (
        SELECT 1 FROM reservas 
        WHERE cancha_id = p_cancha_id 
        AND fecha_reserva = p_fecha
        AND estado IN ('confirmada', 'pendiente')
        AND (
            (hora_inicio < p_hora_fin AND hora_fin > p_hora_inicio) OR
            (hora_inicio >= p_hora_inicio AND hora_inicio < p_hora_fin)
        )
    );
END;
$$;
ALTER FUNCTION public.verificar_disponibilidad_cancha(p_cancha_id integer, p_fecha date, p_hora_inicio time without time zone, p_hora_fin time without time zone) OWNER TO postgres;

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

-- Procedimiento para registrar pago
CREATE OR REPLACE PROCEDURE public.proc_registrar_pago(
    p_reserva_id INTEGER,
    p_monto NUMERIC,
    p_metodo_pago VARCHAR(50),
    p_observaciones TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cliente_id INTEGER;
    v_pago_id INTEGER;
BEGIN
    -- Obtener el cliente_id de la reserva
    SELECT cliente_id INTO v_cliente_id
    FROM reservas
    WHERE id = p_reserva_id;
    
    -- Verificar que la reserva existe
    IF v_cliente_id IS NULL THEN
        RAISE EXCEPTION 'La reserva con ID % no existe', p_reserva_id;
    END IF;
    
    -- Insertar el pago
    INSERT INTO pagos (
        reserva_id,
        cliente_id,
        monto,
        metodo_pago,
        estado,
        observaciones,
        fecha_pago,
        fecha_creacion,
        fecha_actualizacion
    ) VALUES (
        p_reserva_id,
        v_cliente_id,
        p_monto,
        p_metodo_pago,
        'Completado',
        p_observaciones,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    ) RETURNING id INTO v_pago_id;
    
    -- Actualizar el estado de la reserva a 'Pagada'
    UPDATE reservas 
    SET estado = 'Pagada',
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = p_reserva_id;
    
    -- Registrar en auditoría
    INSERT INTO auditoria (
        tabla,
        tipo_accion,
        registro_id,
        usuario_id,
        detalles,
        resultado,
        ip_address,
        fecha_hora
    ) VALUES (
        'pagos',
        'INSERT',
        v_pago_id,
        COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
        'Pago registrado automáticamente - Reserva: ' || p_reserva_id || ', Cliente: ' || v_cliente_id || ', Monto: ' || p_monto || ', Método: ' || p_metodo_pago,
        'SUCCESS',
        '127.0.0.1',
        CURRENT_TIMESTAMP
    );
    
    COMMIT;
    
    RAISE NOTICE 'Pago registrado exitosamente con ID: %', v_pago_id;
END;
$$;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger para actualizar fecha de tipos de cancha
CREATE TRIGGER trigger_actualizar_fecha_tipos_cancha 
    BEFORE UPDATE ON public.tipos_cancha 
    FOR EACH ROW 
    EXECUTE FUNCTION public.actualizar_fecha_tipos_cancha();

-- Trigger para auditoría de canchas
CREATE TRIGGER trigger_auditoria_canchas 
    AFTER INSERT OR DELETE OR UPDATE ON public.canchas 
    FOR EACH ROW 
    EXECUTE FUNCTION public.registrar_auditoria_automatica();

-- Trigger para auditoría de clientes
CREATE TRIGGER trigger_auditoria_clientes 
    AFTER INSERT OR DELETE OR UPDATE ON public.clientes 
    FOR EACH ROW 
    EXECUTE FUNCTION public.registrar_auditoria_automatica();

-- Trigger para auditoría de reservas
CREATE TRIGGER trigger_auditoria_reservas 
    AFTER INSERT OR DELETE OR UPDATE ON public.reservas 
    FOR EACH ROW 
    EXECUTE FUNCTION public.registrar_auditoria_automatica();

-- Trigger para auditoría de tipos de cancha
CREATE TRIGGER trigger_auditoria_tipos_cancha 
    AFTER INSERT OR DELETE OR UPDATE ON public.tipos_cancha 
    FOR EACH ROW 
    EXECUTE FUNCTION public.registrar_auditoria_automatica();

-- Trigger para auditoría de usuarios
CREATE TRIGGER trigger_auditoria_usuarios 
    AFTER INSERT OR DELETE OR UPDATE ON public.usuarios 
    FOR EACH ROW 
    EXECUTE FUNCTION public.registrar_auditoria_automatica();

-- Trigger para actualizar fecha de canchas
CREATE TRIGGER update_canchas_updated_at 
    BEFORE UPDATE ON public.canchas 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para actualizar fecha de clientes
CREATE TRIGGER update_clientes_updated_at 
    BEFORE UPDATE ON public.clientes 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para actualizar fecha de pagos
CREATE TRIGGER update_pagos_updated_at 
    BEFORE UPDATE ON public.pagos 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para actualizar fecha de reservas
CREATE TRIGGER update_reservas_updated_at 
    BEFORE UPDATE ON public.reservas 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para actualizar fecha de tipos de cancha
CREATE TRIGGER update_tipos_cancha_updated_at 
    BEFORE UPDATE ON public.tipos_cancha 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para actualizar fecha de usuarios
CREATE TRIGGER update_usuarios_updated_at 
    BEFORE UPDATE ON public.usuarios 
    FOR EACH ROW 
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- VISTAS
-- =====================================================

-- Vista completa de canchas
CREATE VIEW public.vista_canchas_completa AS
 SELECT ca.id,
    ca.nombre,
    ca.tipo_deporte,
    ca.capacidad,
    ca.precio_hora,
    ca.estado,
    ca.horario_apertura,
    ca.horario_cierre,
    ca.descripcion,
    ca.fecha_creacion,
    ca.fecha_actualizacion,
    count(r.id) AS total_reservas,
    COALESCE(sum((r.duracion * ca.precio_hora)), (0)::numeric) AS ingresos_totales
   FROM (public.canchas ca
     LEFT JOIN public.reservas r ON (((ca.id = r.cancha_id) AND ((r.estado)::text = 'Confirmada'::text))))
  GROUP BY ca.id, ca.nombre, ca.tipo_deporte, ca.capacidad, ca.precio_hora, ca.estado, ca.horario_apertura, ca.horario_cierre, ca.descripcion, ca.fecha_creacion, ca.fecha_actualizacion;
-- ALTER VIEW public.vista_canchas_completa OWNER TO admin_reservas;

-- Vista completa de clientes
CREATE VIEW public.vista_clientes_completa AS
 SELECT c.id,
    c.nombre,
    c.apellido,
    c.email,
    c.telefono,
    c.direccion,
    c.fecha_nacimiento,
    c.estado,
    c.fecha_registro,
    c.fecha_actualizacion,
    count(r.id) AS total_reservas,
    COALESCE(sum(p.monto), (0)::numeric) AS total_pagado
   FROM ((public.clientes c
     LEFT JOIN public.reservas r ON ((c.id = r.cliente_id)))
     LEFT JOIN public.pagos p ON (((c.id = p.cliente_id) AND ((p.estado)::text = 'Completado'::text))))
  GROUP BY c.id, c.nombre, c.apellido, c.email, c.telefono, c.direccion, c.fecha_nacimiento, c.estado, c.fecha_registro, c.fecha_actualizacion;
-- ALTER VIEW public.vista_clientes_completa OWNER TO admin_reservas;

-- Vista completa de pagos
CREATE VIEW public.vista_pagos_completa AS
 SELECT p.id,
    p.reserva_id,
    p.cliente_id,
    c.nombre AS nombre_cliente,
    c.apellido AS apellido_cliente,
    c.email AS email_cliente,
    c.telefono AS telefono_cliente,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    ca.nombre AS nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) AS precio_total_reserva,
    p.monto,
    p.metodo_pago,
    p.estado AS estado_pago,
    p.fecha_pago,
    p.observaciones AS observaciones_pago,
    p.fecha_creacion,
    p.fecha_actualizacion
   FROM (((public.pagos p
     JOIN public.clientes c ON ((p.cliente_id = c.id)))
     JOIN public.reservas r ON ((p.reserva_id = r.id)))
     JOIN public.canchas ca ON ((r.cancha_id = ca.id)));
-- ALTER VIEW public.vista_pagos_completa OWNER TO admin_reservas;

-- Vista completa de reservas
CREATE VIEW public.vista_reservas_completa AS
 SELECT r.id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado,
    r.observaciones,
    c.nombre AS nombre_cliente,
    c.apellido AS apellido_cliente,
    c.email AS email_cliente,
    c.telefono AS telefono_cliente,
    ca.nombre AS nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) AS precio_total,
    r.fecha_creacion,
    r.fecha_actualizacion
   FROM ((public.reservas r
     JOIN public.clientes c ON ((r.cliente_id = c.id)))
     JOIN public.canchas ca ON ((r.cancha_id = ca.id)));
-- ALTER VIEW public.vista_reservas_completa OWNER TO admin_reservas;

-- Vista de reservas con pagos
CREATE VIEW public.vista_reservas_con_pagos AS
 SELECT r.id,
    r.cliente_id,
    c.nombre AS nombre_cliente,
    c.apellido AS apellido_cliente,
    r.cancha_id,
    ca.nombre AS nombre_cancha,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado AS estado_reserva,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) AS precio_total,
    COALESCE(sum(p.monto), (0)::numeric) AS total_pagado,
    ((r.duracion * ca.precio_hora) - COALESCE(sum(p.monto), (0)::numeric)) AS saldo_pendiente,
        CASE
            WHEN (COALESCE(sum(p.monto), (0)::numeric) >= (r.duracion * ca.precio_hora)) THEN 'Pagado'::text
            WHEN (COALESCE(sum(p.monto), (0)::numeric) > (0)::numeric) THEN 'Pago Parcial'::text
            ELSE 'Sin Pago'::text
        END AS estado_pago,
    r.fecha_creacion,
    r.fecha_actualizacion
   FROM (((public.reservas r
     JOIN public.clientes c ON ((r.cliente_id = c.id)))
     JOIN public.canchas ca ON ((r.cancha_id = ca.id)))
     LEFT JOIN public.pagos p ON (((r.id = p.reserva_id) AND ((p.estado)::text = 'Completado'::text))))
  GROUP BY r.id, r.cliente_id, c.nombre, c.apellido, r.cancha_id, ca.nombre, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion, r.estado, ca.precio_hora, r.fecha_creacion, r.fecha_actualizacion;
-- ALTER VIEW public.vista_reservas_con_pagos OWNER TO admin_reservas;

-- Vista de canchas más usadas (para reportes)
CREATE VIEW public.vista_canchas_mas_usadas AS
SELECT 
    c.id,
    c.nombre,
    c.tipo_deporte,
    c.capacidad,
    c.precio_hora,
    c.estado,
    COUNT(r.id) as total_reservas,
    COALESCE(SUM(r.duracion), 0) as horas_totales,
    COALESCE(SUM(r.duracion * c.precio_hora), 0) as ingresos_totales
FROM canchas c
LEFT JOIN reservas r ON c.id = r.cancha_id AND r.estado = 'Confirmada'
GROUP BY c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora, c.estado
ORDER BY total_reservas DESC;

-- Vista de canchas que más recaudan (para reportes)
CREATE VIEW public.vista_canchas_mas_recaudan AS
SELECT 
    c.id,
    c.nombre,
    c.tipo_deporte,
    c.capacidad,
    c.precio_hora,
    c.estado,
    COUNT(r.id) as total_reservas,
    COALESCE(SUM(r.duracion), 0) as horas_totales,
    COALESCE(SUM(r.duracion * c.precio_hora), 0) as ingresos_totales
FROM canchas c
LEFT JOIN reservas r ON c.id = r.cancha_id AND r.estado = 'Confirmada'
GROUP BY c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora, c.estado
ORDER BY ingresos_totales DESC;

-- Vista de reporte de reservas
CREATE VIEW public.vista_reporte_reservas AS
SELECT 
    r.id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado,
    r.observaciones,
    c.nombre as nombre_cliente,
    c.apellido as apellido_cliente,
    c.email as email_cliente,
    c.telefono as telefono_cliente,
    ca.nombre as nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) as precio_total_calculado,
    tc.nombre as tipo_cancha_nombre,
    r.fecha_creacion,
    r.fecha_actualizacion
FROM reservas r
JOIN clientes c ON r.cliente_id = c.id
JOIN canchas ca ON r.cancha_id = ca.id
LEFT JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
ORDER BY r.fecha_reserva DESC, r.hora_inicio;

-- Vista de reporte de ingresos
CREATE VIEW public.vista_reporte_ingresos AS
SELECT 
    p.id,
    p.fecha_pago,
    p.monto,
    p.metodo_pago,
    p.estado as estado_pago,
    p.observaciones,
    c.nombre as nombre_cliente,
    c.apellido as apellido_cliente,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    ca.nombre as nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) as precio_total_reserva,
    STRING_AGG(DISTINCT p.metodo_pago, ', ') as metodos_pago_utilizados,
    p.fecha_creacion,
    p.fecha_actualizacion
FROM pagos p
JOIN clientes c ON p.cliente_id = c.id
JOIN reservas r ON p.reserva_id = r.id
JOIN canchas ca ON r.cancha_id = ca.id
GROUP BY p.id, p.fecha_pago, p.monto, p.metodo_pago, p.estado, p.observaciones, 
         c.nombre, c.apellido, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion,
         ca.nombre, ca.tipo_deporte, ca.precio_hora, p.fecha_creacion, p.fecha_actualizacion
ORDER BY p.fecha_pago DESC;

-- Vista de canchas disponibles
CREATE VIEW public.vista_canchas_disponibles AS
SELECT 
    c.id,
    c.nombre,
    c.tipo_deporte,
    c.capacidad,
    c.precio_hora,
    c.estado,
    c.horario_apertura,
    c.horario_cierre,
    c.descripcion,
    tc.nombre as tipo_cancha_nombre,
    tc.descripcion as tipo_cancha_descripcion,
    tc.precio_por_hora as precio_tipo_cancha,
    COUNT(r.id) as reservas_activas,
    COALESCE(SUM(CASE WHEN r.estado = 'Confirmada' THEN 1 ELSE 0 END), 0) as reservas_confirmadas,
    COALESCE(SUM(CASE WHEN r.estado = 'Pendiente' THEN 1 ELSE 0 END), 0) as reservas_pendientes,
    c.fecha_creacion,
    c.fecha_actualizacion
FROM canchas c
LEFT JOIN tipos_cancha tc ON c.tipo_cancha_id = tc.id
LEFT JOIN reservas r ON c.id = r.cancha_id AND r.fecha_reserva >= CURRENT_DATE
GROUP BY c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora, c.estado,
         c.horario_apertura, c.horario_cierre, c.descripcion, tc.nombre, tc.descripcion,
         tc.precio_por_hora, c.fecha_creacion, c.fecha_actualizacion
ORDER BY c.nombre;

-- =====================================================
-- VISTAS PARA GESTIÓN DE PAGOS (USAN PROCEDIMIENTOS ALMACENADOS)
-- =====================================================

-- Vista de reservas pendientes de pago
CREATE VIEW public.vista_reservas_pendientes_pago AS
SELECT 
    r.id as reserva_id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado as estado_reserva,
    r.observaciones as observaciones_reserva,
    c.id as cliente_id,
    c.nombre as nombre_cliente,
    c.apellido as apellido_cliente,
    c.email as email_cliente,
    c.telefono as telefono_cliente,
    ca.id as cancha_id,
    ca.nombre as nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) as precio_total_calculado,
    COALESCE(SUM(p.monto), 0) as total_pagado,
    ((r.duracion * ca.precio_hora) - COALESCE(SUM(p.monto), 0)) as saldo_pendiente,
    CASE 
        WHEN COALESCE(SUM(p.monto), 0) >= (r.duracion * ca.precio_hora) THEN 'Pagado'
        WHEN COALESCE(SUM(p.monto), 0) > 0 THEN 'Pago Parcial'
        ELSE 'Sin Pago'
    END as estado_pago,
    r.fecha_creacion,
    r.fecha_actualizacion
FROM reservas r
JOIN clientes c ON r.cliente_id = c.id
JOIN canchas ca ON r.cancha_id = ca.id
LEFT JOIN pagos p ON r.id = p.reserva_id AND p.estado = 'Completado'
WHERE r.estado IN ('Confirmada', 'Pendiente')
GROUP BY r.id, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion, r.estado, r.observaciones,
         c.id, c.nombre, c.apellido, c.email, c.telefono,
         ca.id, ca.nombre, ca.tipo_deporte, ca.precio_hora, r.fecha_creacion, r.fecha_actualizacion
HAVING COALESCE(SUM(p.monto), 0) < (r.duracion * ca.precio_hora)
ORDER BY r.fecha_reserva DESC, r.hora_inicio;

-- Vista de historial de pagos con detalles completos
CREATE VIEW public.vista_historial_pagos AS
SELECT 
    p.id as pago_id,
    p.fecha_pago,
    p.monto,
    p.metodo_pago,
    p.estado as estado_pago,
    p.observaciones as observaciones_pago,
    r.id as reserva_id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado as estado_reserva,
    c.id as cliente_id,
    c.nombre as nombre_cliente,
    c.apellido as apellido_cliente,
    c.email as email_cliente,
    c.telefono as telefono_cliente,
    ca.id as cancha_id,
    ca.nombre as nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) as precio_total_reserva,
    p.fecha_creacion,
    p.fecha_actualizacion
FROM pagos p
JOIN reservas r ON p.reserva_id = r.id
JOIN clientes c ON p.cliente_id = c.id
JOIN canchas ca ON r.cancha_id = ca.id
ORDER BY p.fecha_pago DESC, p.fecha_creacion DESC;

-- Vista de resumen de pagos por período
CREATE VIEW public.vista_resumen_pagos_periodo AS
SELECT 
    DATE_TRUNC('month', p.fecha_pago) as mes,
    COUNT(p.id) as total_pagos,
    SUM(p.monto) as total_recaudado,
    AVG(p.monto) as promedio_pago,
    COUNT(DISTINCT p.cliente_id) as clientes_unicos,
    COUNT(DISTINCT r.cancha_id) as canchas_utilizadas,
    STRING_AGG(DISTINCT p.metodo_pago, ', ') as metodos_pago_utilizados,
    COUNT(CASE WHEN p.estado = 'Completado' THEN 1 END) as pagos_completados,
    COUNT(CASE WHEN p.estado = 'Pendiente' THEN 1 END) as pagos_pendientes,
    COUNT(CASE WHEN p.estado = 'Cancelado' THEN 1 END) as pagos_cancelados
FROM pagos p
JOIN reservas r ON p.reserva_id = r.id
GROUP BY DATE_TRUNC('month', p.fecha_pago)
ORDER BY mes DESC;

-- Vista de pagos pendientes por cliente (CORREGIDA)
CREATE VIEW public.vista_pagos_pendientes_cliente AS
WITH reservas_con_pagos AS (
    SELECT 
        c.id as cliente_id,
        c.nombre as nombre_cliente,
        c.apellido as apellido_cliente,
        c.email as email_cliente,
        c.telefono as telefono_cliente,
        r.id as reserva_id,
        r.estado as estado_reserva,
        r.duracion,
        ca.precio_hora,
        (r.duracion * ca.precio_hora) as precio_total,
        COALESCE(SUM(p.monto), 0) as total_pagado
    FROM clientes c
    JOIN reservas r ON c.id = r.cliente_id
    JOIN canchas ca ON r.cancha_id = ca.id
    LEFT JOIN pagos p ON r.id = p.reserva_id AND p.estado = 'Completado'
    GROUP BY c.id, c.nombre, c.apellido, c.email, c.telefono, r.id, r.estado, r.duracion, ca.precio_hora
)
SELECT 
    cliente_id,
    nombre_cliente,
    apellido_cliente,
    email_cliente,
    telefono_cliente,
    COUNT(reserva_id) as total_reservas,
    COUNT(CASE WHEN estado_reserva = 'Confirmada' THEN 1 END) as reservas_confirmadas,
    COUNT(CASE WHEN estado_reserva = 'Pendiente' THEN 1 END) as reservas_pendientes,
    SUM(precio_total) as total_debido,
    SUM(total_pagado) as total_pagado,
    (SUM(precio_total) - SUM(total_pagado)) as saldo_pendiente,
    COUNT(CASE WHEN total_pagado < precio_total THEN 1 END) as reservas_sin_pagar_completamente
FROM reservas_con_pagos
GROUP BY cliente_id, nombre_cliente, apellido_cliente, email_cliente, telefono_cliente
HAVING (SUM(precio_total) - SUM(total_pagado)) > 0
ORDER BY saldo_pendiente DESC;

-- =====================================================
-- PERMISOS PARA FUNCIONES Y PROCEDIMIENTOS
-- =====================================================

-- Permisos para funciones
GRANT ALL ON FUNCTION public.actualizar_fecha_tipos_cancha() TO admin_reservas;
GRANT ALL ON FUNCTION public.update_updated_at_column() TO admin_reservas;

-- Permisos para procedimientos
GRANT EXECUTE ON PROCEDURE public.proc_registrar_pago TO admin_reservas, operador_reservas;

-- Permisos para vistas
GRANT ALL ON TABLE public.vista_canchas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_completa TO consultor_reservas;

GRANT ALL ON TABLE public.vista_clientes_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_clientes_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_clientes_completa TO consultor_reservas;

GRANT ALL ON TABLE public.vista_pagos_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_pagos_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_pagos_completa TO consultor_reservas;

GRANT ALL ON TABLE public.vista_reservas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_completa TO consultor_reservas;

GRANT ALL ON TABLE public.vista_reservas_con_pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_con_pagos TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_con_pagos TO consultor_reservas;

-- Permisos para vistas de reportes (no disponibles para consultor_reservas)
GRANT ALL ON TABLE public.vista_canchas_mas_usadas TO admin_reservas;
GRANT SELECT ON TABLE public.vista_canchas_mas_usadas TO operador_reservas;

GRANT ALL ON TABLE public.vista_canchas_mas_recaudan TO admin_reservas;
GRANT SELECT ON TABLE public.vista_canchas_mas_recaudan TO operador_reservas;

GRANT ALL ON TABLE public.vista_reporte_reservas TO admin_reservas;
GRANT SELECT ON TABLE public.vista_reporte_reservas TO operador_reservas;

GRANT ALL ON TABLE public.vista_reporte_ingresos TO admin_reservas;
GRANT SELECT ON TABLE public.vista_reporte_ingresos TO operador_reservas;

GRANT ALL ON TABLE public.vista_canchas_disponibles TO admin_reservas;
GRANT SELECT ON TABLE public.vista_canchas_disponibles TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_disponibles TO consultor_reservas;

-- Permisos para vistas de gestión de pagos (solo admin y operador)
GRANT ALL ON TABLE public.vista_reservas_pendientes_pago TO admin_reservas;
GRANT SELECT ON TABLE public.vista_reservas_pendientes_pago TO operador_reservas;

GRANT ALL ON TABLE public.vista_historial_pagos TO admin_reservas;
GRANT SELECT ON TABLE public.vista_historial_pagos TO operador_reservas;

GRANT ALL ON TABLE public.vista_resumen_pagos_periodo TO admin_reservas;
GRANT SELECT ON TABLE public.vista_resumen_pagos_periodo TO operador_reservas;

GRANT ALL ON TABLE public.vista_pagos_pendientes_cliente TO admin_reservas;
GRANT SELECT ON TABLE public.vista_pagos_pendientes_cliente TO operador_reservas;

-- =====================================================
-- FUNCIONES, PROCEDIMIENTOS, TRIGGERS Y VISTAS COMPLETADOS
-- ===================================================== 