--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: actualizar_cancha(integer, character varying, character varying, integer, numeric, character varying, time without time zone, time without time zone, text, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: actualizar_fecha_tipos_cancha(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_fecha_tipos_cancha() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_fecha_tipos_cancha() OWNER TO postgres;

--
-- Name: crear_cancha(character varying, character varying, integer, numeric, character varying, time without time zone, time without time zone, text, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: crear_reserva(integer, integer, date, time without time zone, time without time zone, text); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: eliminar_cancha(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.eliminar_cancha(p_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM canchas WHERE id = p_id;
    RETURN FOUND;
END;
$$;


ALTER FUNCTION public.eliminar_cancha(p_id integer) OWNER TO postgres;

--
-- Name: obtener_tipos_cancha(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: proc_generar_estadisticas(date, date, character varying); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.proc_generar_estadisticas(IN p_fecha_inicio date DEFAULT NULL::date, IN p_fecha_fin date DEFAULT NULL::date, IN p_tipo_reporte character varying DEFAULT 'mensual'::character varying)
    LANGUAGE plpgsql
    AS $_$
DECLARE
    v_resultado RECORD;
    v_total_reservas INTEGER;
    v_total_ingresos NUMERIC(10,2);
    v_total_clientes INTEGER;
    v_cancha_mas_usada VARCHAR(100);
    v_cliente_mas_frecuente VARCHAR(100);
    v_promedio_duracion DECIMAL(5,2);
BEGIN
    -- Establecer fechas por defecto si no se proporcionan
    IF p_fecha_inicio IS NULL THEN
        p_fecha_inicio := CURRENT_DATE - INTERVAL '30 days';
    END IF;
    
    IF p_fecha_fin IS NULL THEN
        p_fecha_fin := CURRENT_DATE;
    END IF;
    
    -- Validar fechas
    IF p_fecha_inicio > p_fecha_fin THEN
        RAISE EXCEPTION 'La fecha de inicio no puede ser mayor que la fecha de fin';
    END IF;
    
    -- Generar estadísticas según el tipo de reporte
    CASE p_tipo_reporte
        WHEN 'mensual' THEN
            -- Estadísticas mensuales
            SELECT 
                COUNT(*) as total_reservas,
                COALESCE(SUM(r.duracion * c.precio_hora), 0) as total_ingresos,
                COUNT(DISTINCT r.cliente_id) as total_clientes,
                AVG(r.duracion) as promedio_duracion
            INTO v_resultado
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
            AND r.estado IN ('confirmada', 'pagada');
            
            -- Cancha más usada
            SELECT ca.nombre INTO v_cancha_mas_usada
            FROM reservas r
            JOIN canchas ca ON r.cancha_id = ca.id
            WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
            AND r.estado IN ('confirmada', 'pagada')
            GROUP BY ca.id, ca.nombre
            ORDER BY COUNT(*) DESC
            LIMIT 1;
            
            -- Cliente más frecuente
            SELECT CONCAT(c.nombre, ' ', c.apellido) INTO v_cliente_mas_frecuente
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
            AND r.estado IN ('confirmada', 'pagada')
            GROUP BY c.id, c.nombre, c.apellido
            ORDER BY COUNT(*) DESC
            LIMIT 1;
            
        WHEN 'semanal' THEN
            -- Estadísticas semanales
            SELECT 
                COUNT(*) as total_reservas,
                COALESCE(SUM(r.duracion * c.precio_hora), 0) as total_ingresos,
                COUNT(DISTINCT r.cliente_id) as total_clientes,
                AVG(r.duracion) as promedio_duracion
            INTO v_resultado
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
            AND r.estado IN ('confirmada', 'pagada');
            
        WHEN 'diario' THEN
            -- Estadísticas diarias
            SELECT 
                COUNT(*) as total_reservas,
                COALESCE(SUM(r.duracion * c.precio_hora), 0) as total_ingresos,
                COUNT(DISTINCT r.cliente_id) as total_clientes,
                AVG(r.duracion) as promedio_duracion
            INTO v_resultado
            FROM reservas r
            JOIN canchas c ON r.cancha_id = c.id
            WHERE r.fecha_reserva BETWEEN p_fecha_inicio AND p_fecha_fin
            AND r.estado IN ('confirmada', 'pagada');
            
        ELSE
            RAISE EXCEPTION 'Tipo de reporte no válido. Debe ser mensual, semanal o diario';
    END CASE;
    
    -- Mostrar resultados
    RAISE NOTICE '=== REPORTE DE ESTADÍSTICAS ===';
    RAISE NOTICE 'Período: % a %', p_fecha_inicio, p_fecha_fin;
    RAISE NOTICE 'Tipo de reporte: %', p_tipo_reporte;
    RAISE NOTICE 'Total de reservas: %', v_resultado.total_reservas;
    RAISE NOTICE 'Total de ingresos: $%', v_resultado.total_ingresos;
    RAISE NOTICE 'Total de clientes únicos: %', v_resultado.total_clientes;
    RAISE NOTICE 'Promedio de duración: % horas', v_resultado.promedio_duracion;
    
    IF p_tipo_reporte = 'mensual' THEN
        RAISE NOTICE 'Cancha más usada: %', v_cancha_mas_usada;
        RAISE NOTICE 'Cliente más frecuente: %', v_cliente_mas_frecuente;
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO auditoria (
        tabla, tipo_accion, registro_id, usuario_id, detalles, resultado, ip_address, fecha_hora
    ) VALUES (
        'reportes', 'SELECT', NULL, 
        COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
        'Reporte de estadísticas generado: ' || p_tipo_reporte || ' del ' || p_fecha_inicio || ' al ' || p_fecha_fin,
        'SUCCESS', '127.0.0.1', CURRENT_TIMESTAMP
    );
    
    COMMIT;
END;
$_$;


ALTER PROCEDURE public.proc_generar_estadisticas(IN p_fecha_inicio date, IN p_fecha_fin date, IN p_tipo_reporte character varying) OWNER TO postgres;

--
-- Name: proc_gestionar_reserva(character varying, integer, integer, integer, date, time without time zone, time without time zone, text, character varying); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.proc_gestionar_reserva(IN p_accion character varying, IN p_id integer DEFAULT NULL::integer, IN p_cliente_id integer DEFAULT NULL::integer, IN p_cancha_id integer DEFAULT NULL::integer, IN p_fecha_reserva date DEFAULT NULL::date, IN p_hora_inicio time without time zone DEFAULT NULL::time without time zone, IN p_hora_fin time without time zone DEFAULT NULL::time without time zone, IN p_observaciones text DEFAULT NULL::text, IN p_estado character varying DEFAULT 'pendiente'::character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_reserva_id INTEGER;
    v_duracion DECIMAL(10,2);
    v_disponible BOOLEAN;
    v_cliente_existe BOOLEAN;
    v_cancha_existe BOOLEAN;
    v_reserva_existe BOOLEAN;
BEGIN
    -- Validar parámetros de entrada
    IF p_accion IS NULL OR p_accion NOT IN ('CREATE', 'UPDATE', 'CANCEL') THEN
        RAISE EXCEPTION 'Acción no válida. Debe ser CREATE, UPDATE o CANCEL';
    END IF;
    
    -- Verificar que el cliente existe
    SELECT EXISTS(SELECT 1 FROM clientes WHERE id = p_cliente_id) INTO v_cliente_existe;
    IF NOT v_cliente_existe THEN
        RAISE EXCEPTION 'El cliente con ID % no existe', p_cliente_id;
    END IF;
    
    -- Verificar que la cancha existe
    SELECT EXISTS(SELECT 1 FROM canchas WHERE id = p_cancha_id) INTO v_cancha_existe;
    IF NOT v_cancha_existe THEN
        RAISE EXCEPTION 'La cancha con ID % no existe', p_cancha_id;
    END IF;
    
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
    
    CASE p_accion
        WHEN 'CREATE' THEN
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
            
            -- Registrar en auditoría
            INSERT INTO auditoria (
                tabla, tipo_accion, registro_id, usuario_id, detalles, resultado, ip_address, fecha_hora
            ) VALUES (
                'reservas', 'INSERT', v_reserva_id, 
                COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
                'Reserva creada: Cliente ' || p_cliente_id || ', Cancha ' || p_cancha_id || ', Fecha ' || p_fecha_reserva,
                'SUCCESS', '127.0.0.1', CURRENT_TIMESTAMP
            );
            
            RAISE NOTICE 'Reserva creada exitosamente con ID: %', v_reserva_id;
            
        WHEN 'UPDATE' THEN
            -- Verificar que la reserva existe
            SELECT EXISTS(SELECT 1 FROM reservas WHERE id = p_id) INTO v_reserva_existe;
            IF NOT v_reserva_existe THEN
                RAISE EXCEPTION 'La reserva con ID % no existe', p_id;
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
            
            -- Registrar en auditoría
            INSERT INTO auditoria (
                tabla, tipo_accion, registro_id, usuario_id, detalles, resultado, ip_address, fecha_hora
            ) VALUES (
                'reservas', 'UPDATE', p_id, 
                COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
                'Reserva actualizada: Cliente ' || p_cliente_id || ', Cancha ' || p_cancha_id || ', Fecha ' || p_fecha_reserva,
                'SUCCESS', '127.0.0.1', CURRENT_TIMESTAMP
            );
            
            RAISE NOTICE 'Reserva actualizada exitosamente';
            
        WHEN 'CANCEL' THEN
            -- Verificar que la reserva existe
            SELECT EXISTS(SELECT 1 FROM reservas WHERE id = p_id) INTO v_reserva_existe;
            IF NOT v_reserva_existe THEN
                RAISE EXCEPTION 'La reserva con ID % no existe', p_id;
            END IF;
            
            -- Cancelar la reserva
            UPDATE reservas SET
                estado = 'cancelada',
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = p_id;
            
            -- Registrar en auditoría
            INSERT INTO auditoria (
                tabla, tipo_accion, registro_id, usuario_id, detalles, resultado, ip_address, fecha_hora
            ) VALUES (
                'reservas', 'UPDATE', p_id, 
                COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
                'Reserva cancelada',
                'SUCCESS', '127.0.0.1', CURRENT_TIMESTAMP
            );
            
            RAISE NOTICE 'Reserva cancelada exitosamente';
    END CASE;
    
    COMMIT;
END;
$$;


ALTER PROCEDURE public.proc_gestionar_reserva(IN p_accion character varying, IN p_id integer, IN p_cliente_id integer, IN p_cancha_id integer, IN p_fecha_reserva date, IN p_hora_inicio time without time zone, IN p_hora_fin time without time zone, IN p_observaciones text, IN p_estado character varying) OWNER TO postgres;

--
-- Name: proc_registrar_auditoria_manual(integer, character varying, character varying, integer, text, character varying); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.proc_registrar_auditoria_manual(IN p_usuario_id integer DEFAULT NULL::integer, IN p_tipo_accion character varying DEFAULT 'LOGIN'::character varying, IN p_tabla character varying DEFAULT NULL::character varying, IN p_registro_id integer DEFAULT NULL::integer, IN p_detalles text DEFAULT NULL::text, IN p_ip_address character varying DEFAULT '127.0.0.1'::character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_auditoria_id INTEGER;
    v_usuario_existe BOOLEAN;
    v_tabla_existe BOOLEAN;
BEGIN
    -- Validar parámetros de entrada
    IF p_tipo_accion IS NULL OR p_tipo_accion NOT IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'LOGIN', 'LOGOUT', 'ERROR') THEN
        RAISE EXCEPTION 'Tipo de acción no válido. Debe ser INSERT, UPDATE, DELETE, SELECT, LOGIN, LOGOUT o ERROR';
    END IF;
    
    -- Verificar que el usuario existe (si se proporciona)
    IF p_usuario_id IS NOT NULL THEN
        SELECT EXISTS(SELECT 1 FROM usuarios WHERE id = p_usuario_id) INTO v_usuario_existe;
        IF NOT v_usuario_existe THEN
            RAISE EXCEPTION 'El usuario con ID % no existe', p_usuario_id;
        END IF;
    END IF;
    
    -- Verificar que la tabla existe (solo para acciones de tabla)
    IF p_tipo_accion IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT') AND p_tabla IS NOT NULL THEN
        SELECT EXISTS(
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = p_tabla
        ) INTO v_tabla_existe;
        
        IF NOT v_tabla_existe THEN
            RAISE EXCEPTION 'La tabla % no existe', p_tabla;
        END IF;
    END IF;
    
    -- Validar IP address
    IF p_ip_address IS NULL OR p_ip_address = '' THEN
        p_ip_address := '127.0.0.1';
    END IF;
    
    -- Insertar registro de auditoría
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
        p_usuario_id,
        p_tipo_accion,
        p_tabla,
        p_registro_id,
        p_detalles,
        'SUCCESS',
        p_ip_address,
        CURRENT_TIMESTAMP
    ) RETURNING id INTO v_auditoria_id;
    
    RAISE NOTICE 'Registro de auditoría creado con ID: %', v_auditoria_id;
    
    COMMIT;
END;
$$;


ALTER PROCEDURE public.proc_registrar_auditoria_manual(IN p_usuario_id integer, IN p_tipo_accion character varying, IN p_tabla character varying, IN p_registro_id integer, IN p_detalles text, IN p_ip_address character varying) OWNER TO postgres;

--
-- Name: proc_registrar_pago(integer, numeric, character varying, text); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.proc_registrar_pago(IN p_reserva_id integer, IN p_monto numeric, IN p_metodo_pago character varying, IN p_observaciones text DEFAULT NULL::text)
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
    
    -- Registrar en auditoría (usando la estructura correcta de la tabla)
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
    
    RAISE NOTICE 'Pago registrado exitosamente con ID: %', v_pago_id;
END;
$$;


ALTER PROCEDURE public.proc_registrar_pago(IN p_reserva_id integer, IN p_monto numeric, IN p_metodo_pago character varying, IN p_observaciones text) OWNER TO postgres;

--
-- Name: proc_validar_y_limpiar_datos(character varying, character varying); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.proc_validar_y_limpiar_datos(IN p_tabla character varying, IN p_accion character varying DEFAULT 'VALIDATE'::character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_tabla_existe BOOLEAN;
    v_registros_invalidos INTEGER := 0;
    v_registros_limpiados INTEGER := 0;
    v_backup_creado BOOLEAN := FALSE;
    v_sql TEXT;
    v_resultado RECORD;
BEGIN
    -- Validar parámetros de entrada
    IF p_accion NOT IN ('VALIDATE', 'CLEAN', 'BACKUP') THEN
        RAISE EXCEPTION 'Acción no válida. Debe ser VALIDATE, CLEAN o BACKUP';
    END IF;
    
    -- Verificar que la tabla existe
    SELECT EXISTS(
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = p_tabla
    ) INTO v_tabla_existe;
    
    IF NOT v_tabla_existe THEN
        RAISE EXCEPTION 'La tabla % no existe', p_tabla;
    END IF;
    
    -- Ejecutar acciones según el parámetro
    CASE p_accion
        WHEN 'VALIDATE' THEN
            RAISE NOTICE '=== VALIDACIÓN DE DATOS EN TABLA: % ===', p_tabla;
            
            -- Validar registros según la tabla
            CASE p_tabla
                WHEN 'clientes' THEN
                    -- Validar clientes con email duplicado
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM clientes c1
                    WHERE EXISTS (
                        SELECT 1 FROM clientes c2 
                        WHERE c2.email = c1.email AND c2.id != c1.id
                    );
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % clientes con email duplicado', v_registros_invalidos;
                    END IF;
                    
                    -- Validar clientes con teléfono duplicado
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM clientes c1
                    WHERE EXISTS (
                        SELECT 1 FROM clientes c2 
                        WHERE c2.telefono = c1.telefono AND c2.id != c1.id
                    );
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % clientes con teléfono duplicado', v_registros_invalidos;
                    END IF;
                    
                WHEN 'reservas' THEN
                    -- Validar reservas con fechas pasadas
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM reservas
                    WHERE fecha_reserva < CURRENT_DATE AND estado IN ('pendiente', 'confirmada');
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % reservas con fechas pasadas', v_registros_invalidos;
                    END IF;
                    
                    -- Validar reservas con duración inválida
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM reservas
                    WHERE duracion <= 0 OR duracion > 24;
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % reservas con duración inválida', v_registros_invalidos;
                    END IF;
                    
                WHEN 'canchas' THEN
                    -- Validar canchas con precios negativos
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM canchas
                    WHERE precio_hora < 0;
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % canchas con precios negativos', v_registros_invalidos;
                    END IF;
                    
                WHEN 'pagos' THEN
                    -- Validar pagos con montos negativos
                    SELECT COUNT(*) INTO v_registros_invalidos
                    FROM pagos
                    WHERE monto < 0;
                    
                    IF v_registros_invalidos > 0 THEN
                        RAISE NOTICE 'Se encontraron % pagos con montos negativos', v_registros_invalidos;
                    END IF;
                    
                ELSE
                    RAISE NOTICE 'Validación específica no implementada para la tabla %', p_tabla;
            END CASE;
            
        WHEN 'CLEAN' THEN
            RAISE NOTICE '=== LIMPIEZA DE DATOS EN TABLA: % ===', p_tabla;
            
            -- Limpiar datos según la tabla
            CASE p_tabla
                WHEN 'clientes' THEN
                    -- Limpiar emails duplicados (mantener el más reciente)
                    WITH duplicados AS (
                        SELECT id, email, fecha_registro,
                               ROW_NUMBER() OVER (PARTITION BY email ORDER BY fecha_registro DESC) as rn
                        FROM clientes
                        WHERE email IS NOT NULL
                    )
                    DELETE FROM clientes 
                    WHERE id IN (
                        SELECT id FROM duplicados WHERE rn > 1
                    );
                    
                    GET DIAGNOSTICS v_registros_limpiados = ROW_COUNT;
                    RAISE NOTICE 'Se eliminaron % registros duplicados de clientes', v_registros_limpiados;
                    
                WHEN 'reservas' THEN
                    -- Cancelar reservas con fechas pasadas
                    UPDATE reservas 
                    SET estado = 'cancelada', fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE fecha_reserva < CURRENT_DATE AND estado IN ('pendiente', 'confirmada');
                    
                    GET DIAGNOSTICS v_registros_limpiados = ROW_COUNT;
                    RAISE NOTICE 'Se cancelaron % reservas con fechas pasadas', v_registros_limpiados;
                    
                WHEN 'canchas' THEN
                    -- Corregir precios negativos
                    UPDATE canchas 
                    SET precio_hora = 0, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE precio_hora < 0;
                    
                    GET DIAGNOSTICS v_registros_limpiados = ROW_COUNT;
                    RAISE NOTICE 'Se corrigieron % canchas con precios negativos', v_registros_limpiados;
                    
                WHEN 'pagos' THEN
                    -- Corregir montos negativos
                    UPDATE pagos 
                    SET monto = 0, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE monto < 0;
                    
                    GET DIAGNOSTICS v_registros_limpiados = ROW_COUNT;
                    RAISE NOTICE 'Se corrigieron % pagos con montos negativos', v_registros_limpiados;
                    
                ELSE
                    RAISE NOTICE 'Limpieza específica no implementada para la tabla %', p_tabla;
            END CASE;
            
        WHEN 'BACKUP' THEN
            RAISE NOTICE '=== CREACIÓN DE BACKUP DE TABLA: % ===', p_tabla;
            
            -- Crear tabla de backup
            v_sql := format('CREATE TABLE IF NOT EXISTS %I_backup_%s AS SELECT * FROM %I', 
                           p_tabla, to_char(CURRENT_TIMESTAMP, 'YYYYMMDD_HH24MISS'), p_tabla);
            EXECUTE v_sql;
            
            v_backup_creado := TRUE;
            RAISE NOTICE 'Backup creado exitosamente: %_backup_%s', 
                        p_tabla, to_char(CURRENT_TIMESTAMP, 'YYYYMMDD_HH24MISS');
    END CASE;
    
    -- Registrar en auditoría
    INSERT INTO auditoria (
        tabla, tipo_accion, registro_id, usuario_id, detalles, resultado, ip_address, fecha_hora
    ) VALUES (
        p_tabla, p_accion, NULL, 
        COALESCE(current_setting('app.current_user_id', true)::INTEGER, 1),
        'Procedimiento de validación/limpieza ejecutado: ' || p_accion || ' en tabla ' || p_tabla,
        'SUCCESS', '127.0.0.1', CURRENT_TIMESTAMP
    );
    
    COMMIT;
END;
$$;


ALTER PROCEDURE public.proc_validar_y_limpiar_datos(IN p_tabla character varying, IN p_accion character varying) OWNER TO postgres;

--
-- Name: registrar_auditoria_automatica(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

--
-- Name: verificar_disponibilidad_cancha(integer, date, time without time zone, time without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditoria (
    id integer NOT NULL,
    usuario_id integer,
    tipo_accion character varying(20) NOT NULL,
    tabla character varying(50) NOT NULL,
    registro_id integer,
    detalles text,
    resultado character varying(20) DEFAULT 'SUCCESS'::character varying NOT NULL,
    ip_address character varying(45),
    fecha_hora timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.auditoria OWNER TO postgres;

--
-- Name: auditoria_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auditoria_id_seq OWNER TO postgres;

--
-- Name: auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditoria_id_seq OWNED BY public.auditoria.id;


--
-- Name: canchas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.canchas (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    tipo_deporte character varying(50) NOT NULL,
    capacidad integer DEFAULT 0,
    precio_hora numeric(10,2) NOT NULL,
    estado character varying(20) DEFAULT 'Activa'::character varying NOT NULL,
    horario_apertura time without time zone DEFAULT '06:00:00'::time without time zone NOT NULL,
    horario_cierre time without time zone DEFAULT '22:00:00'::time without time zone NOT NULL,
    descripcion text,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    tipo_cancha_id integer
);


ALTER TABLE public.canchas OWNER TO postgres;

--
-- Name: canchas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.canchas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.canchas_id_seq OWNER TO postgres;

--
-- Name: canchas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.canchas_id_seq OWNED BY public.canchas.id;


--
-- Name: clientes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clientes (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    email character varying(100),
    telefono character varying(20),
    direccion text,
    fecha_nacimiento date,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.clientes OWNER TO postgres;

--
-- Name: clientes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clientes_id_seq OWNER TO postgres;

--
-- Name: clientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clientes_id_seq OWNED BY public.clientes.id;


--
-- Name: pagos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pagos (
    id integer NOT NULL,
    reserva_id integer NOT NULL,
    cliente_id integer NOT NULL,
    monto numeric(10,2) NOT NULL,
    metodo_pago character varying(50) NOT NULL,
    estado character varying(20) DEFAULT 'Pendiente'::character varying NOT NULL,
    fecha_pago date NOT NULL,
    observaciones text,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.pagos OWNER TO postgres;

--
-- Name: pagos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pagos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pagos_id_seq OWNER TO postgres;

--
-- Name: pagos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pagos_id_seq OWNED BY public.pagos.id;


--
-- Name: reservas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservas (
    id integer NOT NULL,
    cliente_id integer NOT NULL,
    cancha_id integer NOT NULL,
    fecha_reserva date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    duracion numeric(4,2) NOT NULL,
    estado character varying(20) DEFAULT 'Pendiente'::character varying NOT NULL,
    observaciones text,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.reservas OWNER TO postgres;

--
-- Name: reservas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservas_id_seq OWNER TO postgres;

--
-- Name: reservas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservas_id_seq OWNED BY public.reservas.id;


--
-- Name: tipos_cancha; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipos_cancha (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    precio_por_hora numeric(10,2) DEFAULT 0.00 NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tipos_cancha OWNER TO postgres;

--
-- Name: tipos_cancha_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipos_cancha_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipos_cancha_id_seq OWNER TO postgres;

--
-- Name: tipos_cancha_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipos_cancha_id_seq OWNED BY public.tipos_cancha.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    rol character varying(50) DEFAULT 'consultor_reservas'::character varying NOT NULL,
    estado character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    telefono character varying(20),
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: vista_canchas_completa; Type: VIEW; Schema: public; Owner: root123
--

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


ALTER VIEW public.vista_canchas_completa OWNER TO root123;

--
-- Name: vista_canchas_disponibles; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_canchas_disponibles AS
 SELECT c.id,
    c.nombre,
    c.tipo_deporte,
    c.capacidad,
    c.precio_hora,
    c.estado,
    c.horario_apertura,
    c.horario_cierre,
    c.descripcion AS descripcion_cancha,
    tc.nombre AS tipo_cancha_nombre,
    tc.descripcion AS tipo_cancha_descripcion,
    tc.precio_por_hora AS precio_tipo_cancha,
    tc.estado AS estado_tipo_cancha,
    c.fecha_creacion,
    c.fecha_actualizacion
   FROM (public.canchas c
     LEFT JOIN public.tipos_cancha tc ON ((c.tipo_cancha_id = tc.id)))
  WHERE ((c.estado)::text = 'Activa'::text)
  ORDER BY c.nombre;


ALTER VIEW public.vista_canchas_disponibles OWNER TO postgres;

--
-- Name: vista_canchas_mas_recaudan; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_canchas_mas_recaudan AS
 SELECT c.id,
    c.nombre,
    c.tipo_deporte,
    c.precio_hora,
    tc.nombre AS tipo_cancha_nombre,
    count(r.id) AS total_reservas,
    COALESCE(sum((r.duracion * c.precio_hora)), (0)::numeric) AS ingresos_totales,
    round(avg((r.duracion * c.precio_hora)), 2) AS promedio_por_reserva,
    COALESCE(sum(r.duracion), (0)::numeric) AS horas_totales_utilizadas,
    round((COALESCE(sum((r.duracion * c.precio_hora)), (0)::numeric) / (NULLIF(count(r.id), 0))::numeric), 2) AS ingreso_promedio_por_reserva
   FROM ((public.canchas c
     LEFT JOIN public.tipos_cancha tc ON ((c.tipo_cancha_id = tc.id)))
     LEFT JOIN public.reservas r ON (((c.id = r.cancha_id) AND ((r.estado)::text = ANY ((ARRAY['Confirmada'::character varying, 'Completada'::character varying])::text[])))))
  WHERE ((c.estado)::text = 'Activa'::text)
  GROUP BY c.id, c.nombre, c.tipo_deporte, c.precio_hora, tc.nombre
  ORDER BY COALESCE(sum((r.duracion * c.precio_hora)), (0)::numeric) DESC, (count(r.id)) DESC;


ALTER VIEW public.vista_canchas_mas_recaudan OWNER TO postgres;

--
-- Name: vista_canchas_mas_usadas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_canchas_mas_usadas AS
 SELECT c.id,
    c.nombre,
    c.tipo_deporte,
    c.precio_hora,
    tc.nombre AS tipo_cancha_nombre,
    count(r.id) AS total_reservas,
    COALESCE(sum((r.duracion * c.precio_hora)), (0)::numeric) AS ingresos_totales,
    round(avg((r.duracion * c.precio_hora)), 2) AS promedio_por_reserva,
    COALESCE(sum(r.duracion), (0)::numeric) AS horas_totales_utilizadas
   FROM ((public.canchas c
     LEFT JOIN public.tipos_cancha tc ON ((c.tipo_cancha_id = tc.id)))
     LEFT JOIN public.reservas r ON (((c.id = r.cancha_id) AND ((r.estado)::text = ANY ((ARRAY['Confirmada'::character varying, 'Completada'::character varying])::text[])))))
  WHERE ((c.estado)::text = 'Activa'::text)
  GROUP BY c.id, c.nombre, c.tipo_deporte, c.precio_hora, tc.nombre
  ORDER BY (count(r.id)) DESC, COALESCE(sum((r.duracion * c.precio_hora)), (0)::numeric) DESC;


ALTER VIEW public.vista_canchas_mas_usadas OWNER TO postgres;

--
-- Name: vista_clientes_completa; Type: VIEW; Schema: public; Owner: root123
--

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


ALTER VIEW public.vista_clientes_completa OWNER TO root123;

--
-- Name: vista_historial_pagos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_historial_pagos AS
 SELECT p.id AS pago_id,
    p.fecha_pago,
    p.monto,
    p.metodo_pago,
    p.estado AS estado_pago,
    p.observaciones AS observaciones_pago,
    r.id AS reserva_id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado AS estado_reserva,
    c.id AS cliente_id,
    c.nombre AS nombre_cliente,
    c.apellido AS apellido_cliente,
    c.email AS email_cliente,
    c.telefono AS telefono_cliente,
    ca.id AS cancha_id,
    ca.nombre AS nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) AS precio_total_reserva,
    p.fecha_creacion,
    p.fecha_actualizacion
   FROM (((public.pagos p
     JOIN public.reservas r ON ((p.reserva_id = r.id)))
     JOIN public.clientes c ON ((p.cliente_id = c.id)))
     JOIN public.canchas ca ON ((r.cancha_id = ca.id)))
  ORDER BY p.fecha_pago DESC, p.fecha_creacion DESC;


ALTER VIEW public.vista_historial_pagos OWNER TO postgres;

--
-- Name: vista_pagos_completa; Type: VIEW; Schema: public; Owner: root123
--

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


ALTER VIEW public.vista_pagos_completa OWNER TO root123;

--
-- Name: vista_pagos_pendientes_cliente; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_pagos_pendientes_cliente AS
 WITH reservas_con_pagos AS (
         SELECT c.id AS cliente_id,
            c.nombre AS nombre_cliente,
            c.apellido AS apellido_cliente,
            c.email AS email_cliente,
            c.telefono AS telefono_cliente,
            r.id AS reserva_id,
            r.estado AS estado_reserva,
            r.duracion,
            ca.precio_hora,
            (r.duracion * ca.precio_hora) AS precio_total,
            COALESCE(sum(p.monto), (0)::numeric) AS total_pagado
           FROM (((public.clientes c
             JOIN public.reservas r ON ((c.id = r.cliente_id)))
             JOIN public.canchas ca ON ((r.cancha_id = ca.id)))
             LEFT JOIN public.pagos p ON (((r.id = p.reserva_id) AND ((p.estado)::text = 'Completado'::text))))
          GROUP BY c.id, c.nombre, c.apellido, c.email, c.telefono, r.id, r.estado, r.duracion, ca.precio_hora
        )
 SELECT cliente_id,
    nombre_cliente,
    apellido_cliente,
    email_cliente,
    telefono_cliente,
    count(reserva_id) AS total_reservas,
    count(
        CASE
            WHEN ((estado_reserva)::text = 'Confirmada'::text) THEN 1
            ELSE NULL::integer
        END) AS reservas_confirmadas,
    count(
        CASE
            WHEN ((estado_reserva)::text = 'Pendiente'::text) THEN 1
            ELSE NULL::integer
        END) AS reservas_pendientes,
    sum(precio_total) AS total_debido,
    sum(total_pagado) AS total_pagado,
    (sum(precio_total) - sum(total_pagado)) AS saldo_pendiente,
    count(
        CASE
            WHEN (total_pagado < precio_total) THEN 1
            ELSE NULL::integer
        END) AS reservas_sin_pagar_completamente
   FROM reservas_con_pagos
  GROUP BY cliente_id, nombre_cliente, apellido_cliente, email_cliente, telefono_cliente
 HAVING ((sum(precio_total) - sum(total_pagado)) > (0)::numeric)
  ORDER BY (sum(precio_total) - sum(total_pagado)) DESC;


ALTER VIEW public.vista_pagos_pendientes_cliente OWNER TO postgres;

--
-- Name: vista_reporte_ingresos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_reporte_ingresos AS
 SELECT r.fecha_reserva AS fecha,
    c.nombre AS cancha,
    c.tipo_deporte,
    tc.nombre AS tipo_cancha_nombre,
    count(r.id) AS total_reservas,
    sum((r.duracion * c.precio_hora)) AS ingresos_del_dia,
    round(avg((r.duracion * c.precio_hora)), 2) AS promedio_por_reserva,
    count(p.id) AS pagos_realizados,
    sum(p.monto) AS monto_cobrado,
    string_agg(DISTINCT (p.metodo_pago)::text, ', '::text) AS metodos_pago_utilizados,
    sum(r.duracion) AS horas_totales_utilizadas
   FROM (((public.reservas r
     JOIN public.canchas c ON ((r.cancha_id = c.id)))
     LEFT JOIN public.tipos_cancha tc ON ((c.tipo_cancha_id = tc.id)))
     LEFT JOIN public.pagos p ON (((r.id = p.reserva_id) AND ((p.estado)::text = 'Completado'::text))))
  WHERE ((r.estado)::text = ANY ((ARRAY['Confirmada'::character varying, 'Completada'::character varying])::text[]))
  GROUP BY r.fecha_reserva, c.id, c.nombre, c.tipo_deporte, tc.nombre
  ORDER BY r.fecha_reserva DESC, (sum((r.duracion * c.precio_hora))) DESC;


ALTER VIEW public.vista_reporte_ingresos OWNER TO postgres;

--
-- Name: vista_reporte_reservas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_reporte_reservas AS
 SELECT r.id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado,
    r.observaciones,
    c.nombre AS nombre_cancha,
    c.tipo_deporte,
    c.precio_hora,
    (r.duracion * c.precio_hora) AS precio_total_calculado,
    (((cl.nombre)::text || ' '::text) || (cl.apellido)::text) AS nombre_cliente,
    cl.email AS email_cliente,
    cl.telefono AS telefono_cliente,
    tc.nombre AS tipo_cancha_nombre,
    tc.precio_por_hora AS precio_tipo_cancha,
    p.estado AS estado_pago,
    p.monto AS monto_pagado,
    p.metodo_pago,
    p.fecha_pago,
    r.fecha_creacion,
    r.fecha_actualizacion
   FROM ((((public.reservas r
     JOIN public.canchas c ON ((r.cancha_id = c.id)))
     JOIN public.clientes cl ON ((r.cliente_id = cl.id)))
     LEFT JOIN public.tipos_cancha tc ON ((c.tipo_cancha_id = tc.id)))
     LEFT JOIN public.pagos p ON ((r.id = p.reserva_id)))
  ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC;


ALTER VIEW public.vista_reporte_reservas OWNER TO postgres;

--
-- Name: vista_reservas_completa; Type: VIEW; Schema: public; Owner: root123
--

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


ALTER VIEW public.vista_reservas_completa OWNER TO root123;

--
-- Name: vista_reservas_con_pagos; Type: VIEW; Schema: public; Owner: root123
--

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


ALTER VIEW public.vista_reservas_con_pagos OWNER TO root123;

--
-- Name: vista_reservas_pendientes_pago; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_reservas_pendientes_pago AS
 SELECT r.id AS reserva_id,
    r.fecha_reserva,
    r.hora_inicio,
    r.hora_fin,
    r.duracion,
    r.estado AS estado_reserva,
    r.observaciones AS observaciones_reserva,
    c.id AS cliente_id,
    c.nombre AS nombre_cliente,
    c.apellido AS apellido_cliente,
    c.email AS email_cliente,
    c.telefono AS telefono_cliente,
    ca.id AS cancha_id,
    ca.nombre AS nombre_cancha,
    ca.tipo_deporte,
    ca.precio_hora,
    (r.duracion * ca.precio_hora) AS precio_total_calculado,
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
  WHERE ((r.estado)::text = ANY ((ARRAY['Confirmada'::character varying, 'Pendiente'::character varying])::text[]))
  GROUP BY r.id, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion, r.estado, r.observaciones, c.id, c.nombre, c.apellido, c.email, c.telefono, ca.id, ca.nombre, ca.tipo_deporte, ca.precio_hora, r.fecha_creacion, r.fecha_actualizacion
 HAVING (COALESCE(sum(p.monto), (0)::numeric) < (r.duracion * ca.precio_hora))
  ORDER BY r.fecha_reserva DESC, r.hora_inicio;


ALTER VIEW public.vista_reservas_pendientes_pago OWNER TO postgres;

--
-- Name: vista_resumen_pagos_periodo; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vista_resumen_pagos_periodo AS
 SELECT date_trunc('month'::text, (p.fecha_pago)::timestamp with time zone) AS mes,
    count(p.id) AS total_pagos,
    sum(p.monto) AS total_recaudado,
    avg(p.monto) AS promedio_pago,
    count(DISTINCT p.cliente_id) AS clientes_unicos,
    count(DISTINCT r.cancha_id) AS canchas_utilizadas,
    string_agg(DISTINCT (p.metodo_pago)::text, ', '::text) AS metodos_pago_utilizados,
    count(
        CASE
            WHEN ((p.estado)::text = 'Completado'::text) THEN 1
            ELSE NULL::integer
        END) AS pagos_completados,
    count(
        CASE
            WHEN ((p.estado)::text = 'Pendiente'::text) THEN 1
            ELSE NULL::integer
        END) AS pagos_pendientes,
    count(
        CASE
            WHEN ((p.estado)::text = 'Cancelado'::text) THEN 1
            ELSE NULL::integer
        END) AS pagos_cancelados
   FROM (public.pagos p
     JOIN public.reservas r ON ((p.reserva_id = r.id)))
  GROUP BY (date_trunc('month'::text, (p.fecha_pago)::timestamp with time zone))
  ORDER BY (date_trunc('month'::text, (p.fecha_pago)::timestamp with time zone)) DESC;


ALTER VIEW public.vista_resumen_pagos_periodo OWNER TO postgres;

--
-- Name: auditoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria ALTER COLUMN id SET DEFAULT nextval('public.auditoria_id_seq'::regclass);


--
-- Name: canchas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas ALTER COLUMN id SET DEFAULT nextval('public.canchas_id_seq'::regclass);


--
-- Name: clientes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);


--
-- Name: pagos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos ALTER COLUMN id SET DEFAULT nextval('public.pagos_id_seq'::regclass);


--
-- Name: reservas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id SET DEFAULT nextval('public.reservas_id_seq'::regclass);


--
-- Name: tipos_cancha id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha ALTER COLUMN id SET DEFAULT nextval('public.tipos_cancha_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria (id, usuario_id, tipo_accion, tabla, registro_id, detalles, resultado, ip_address, fecha_hora) FROM stdin;
1	\N	DELETE	canchas	6	Registro eliminado	SUCCESS	127.0.0.1	2025-08-02 19:27:57.898328
5	\N	UPDATE	reservas	4	Registro actualizado	SUCCESS	127.0.0.1	2025-08-03 16:51:57.211706
6	1	INSERT	pagos	7	Pago registrado automáticamente - Reserva: 4, Cliente: 4, Monto: 70.0, Método: Efectivo	SUCCESS	127.0.0.1	2025-08-03 16:51:57.211706
7	\N	UPDATE	reservas	2	Registro actualizado	SUCCESS	127.0.0.1	2025-08-03 17:17:15.672426
8	1	INSERT	pagos	8	Pago registrado automáticamente - Reserva: 2, Cliente: 2, Monto: 80.0, Método: Efectivo	SUCCESS	127.0.0.1	2025-08-03 17:17:15.672426
9	\N	INSERT	tipos_cancha	32	Nuevo registro creado	SUCCESS	127.0.0.1	2025-08-03 18:12:26.135777
10	\N	UPDATE	canchas	2	Registro actualizado	SUCCESS	127.0.0.1	2025-08-04 13:52:15.050537
\.


--
-- Data for Name: canchas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.canchas (id, nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion, fecha_creacion, fecha_actualizacion, tipo_cancha_id) FROM stdin;
3	Cancha 3 - Basketball	Basketball	50	40.00	Activa	06:00:00	22:00:00	Cancha de basketball con piso de madera	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
4	Cancha 4 - Tennis	Tennis	30	60.00	Activa	06:00:00	22:00:00	Cancha de tennis con superficie de arcilla	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
5	Cancha 5 - Voleibol	Voleibol	40	35.00	Activa	06:00:00	22:00:00	Cancha de voleibol de arena	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
7	prueba 2	Fútbol	50	50.00	Activa	06:00:00	22:00:00	prueba operador	2025-08-01 16:56:27.162001	2025-08-01 16:56:27.162001	15
1	Cancha Elefante	Fútbol	100	50.00	Activa	06:00:00	22:00:00	Cancha de fútbol 11 con césped sintético	2025-07-31 11:20:41.988297	2025-08-01 17:07:43.665966	1
2	Cancha 2 - Fútbol pelota	Fútbol	100	50.00	Activa	06:00:00	22:00:00	Cancha de fútbol 11 con césped sintético	2025-07-31 11:20:41.988297	2025-08-04 13:52:15.050537	1
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clientes (id, nombre, apellido, email, telefono, direccion, fecha_nacimiento, estado, fecha_registro, fecha_actualizacion) FROM stdin;
1	Juan	Pérez	juan.perez@email.com	3001234567	Calle 123 #45-67	1990-05-15	Activo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
2	María	González	maria.gonzalez@email.com	3002345678	Carrera 78 #90-12	1985-08-22	Activo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
3	Carlos	Rodríguez	carlos.rodriguez@email.com	3003456789	Avenida 5 #23-45	1992-12-10	Activo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
4	Ana	López	ana.lopez@email.com	3004567890	Calle 90 #12-34	1988-03-28	Activo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
5	Luis	Martínez	luis.martinez@email.com	3005678901	Carrera 45 #67-89	1995-07-14	Activo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pagos (id, reserva_id, cliente_id, monto, metodo_pago, estado, fecha_pago, observaciones, fecha_creacion, fecha_actualizacion) FROM stdin;
1	1	1	100.00	Efectivo	Completado	2025-07-31	Pago en efectivo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
2	3	3	60.00	Tarjeta de Crédito	Completado	2025-07-31	Pago con tarjeta	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
3	5	5	100.00	Transferencia	Completado	2025-07-31	Transferencia bancaria	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
7	4	4	70.00	Efectivo	Completado	2025-08-03	monedas	2025-08-03 16:51:57.211706	2025-08-03 16:51:57.211706
8	2	2	80.00	Efectivo	Completado	2025-08-03		2025-08-03 17:17:15.672426	2025-08-03 17:17:15.672426
\.


--
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservas (id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, duracion, estado, observaciones, fecha_creacion, fecha_actualizacion) FROM stdin;
1	1	1	2025-08-01	14:00:00	16:00:00	2.00	Confirmada	Partido de fútbol	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
3	3	4	2025-08-03	10:00:00	11:00:00	1.00	Confirmada	Clase de tennis	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
5	5	2	2025-08-04	20:00:00	22:00:00	2.00	Confirmada	Partido nocturno	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
8	4	2	2025-08-02	14:00:00	16:00:00	2.00	pendiente	\N	2025-08-02 19:07:35.906714	2025-08-02 19:07:35.906714
9	2	7	2025-08-02	14:00:00	18:00:00	4.00	pendiente	\N	2025-08-02 19:07:52.007044	2025-08-02 19:07:52.007044
4	4	5	2025-08-01	18:00:00	20:00:00	2.00	Pagada	Torneo de voleibol	2025-07-31 11:20:41.988297	2025-08-03 16:51:57.211706
2	2	3	2025-08-02	16:00:00	18:00:00	2.00	Pagada	Entrenamiento de basketball	2025-07-31 11:20:41.988297	2025-08-03 17:17:15.672426
\.


--
-- Data for Name: tipos_cancha; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_cancha (id, nombre, descripcion, precio_por_hora, estado, fecha_creacion, fecha_actualizacion) FROM stdin;
1	Fútbol 11	Cancha de fútbol para 11 jugadores	50.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
2	Fútbol 7	Cancha de fútbol para 7 jugadores	40.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
3	Basketball	Cancha de baloncesto	35.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
4	Tennis	Cancha de tenis	45.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
5	Voleibol	Cancha de voleibol	30.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
6	Fútbol 5	Cancha de fútbol para 5 jugadores	35.00	Activo	2025-07-31 11:38:53.28448	2025-07-31 11:38:53.28448
13	Tenis	Cancha de tenis	80.00	Activo	2025-07-31 12:45:50.268719	2025-07-31 12:45:50.268719
14	prueba	prueba	50.00	Activo	2025-08-01 16:50:39.002218	2025-08-01 16:50:39.002218
15	prueba 2	prueba 2	50.00	Activo	2025-08-01 16:56:27.150779	2025-08-01 16:56:27.150779
26	Padel	cancha de padel	100.00	Activo	2025-08-02 19:22:47.697449	2025-08-02 19:22:47.697449
32	prueba supabase	prueba supabase	50.00	Activo	2025-08-03 18:12:26.135777	2025-08-03 18:12:26.135777
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, email, password, nombre, apellido, rol, estado, telefono, fecha_creacion, fecha_actualizacion) FROM stdin;
1	admin	admin@sportcourt.com	8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918	Administrador	Sistema	admin_reservas	Activo	\N	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
\.


--
-- Name: auditoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditoria_id_seq', 10, true);


--
-- Name: canchas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.canchas_id_seq', 8, true);


--
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clientes_id_seq', 5, true);


--
-- Name: pagos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pagos_id_seq', 8, true);


--
-- Name: reservas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservas_id_seq', 9, true);


--
-- Name: tipos_cancha_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipos_cancha_id_seq', 32, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);


--
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id);


--
-- Name: canchas canchas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas
    ADD CONSTRAINT canchas_pkey PRIMARY KEY (id);


--
-- Name: clientes clientes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_email_key UNIQUE (email);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (id);


--
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id);


--
-- Name: tipos_cancha tipos_cancha_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha
    ADD CONSTRAINT tipos_cancha_nombre_key UNIQUE (nombre);


--
-- Name: tipos_cancha tipos_cancha_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha
    ADD CONSTRAINT tipos_cancha_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_fecha ON public.auditoria USING btree (fecha_hora);


--
-- Name: idx_auditoria_tabla; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_tabla ON public.auditoria USING btree (tabla);


--
-- Name: idx_auditoria_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_tipo ON public.auditoria USING btree (tipo_accion);


--
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario ON public.auditoria USING btree (usuario_id);


--
-- Name: idx_canchas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_estado ON public.canchas USING btree (estado);


--
-- Name: idx_canchas_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_tipo ON public.canchas USING btree (tipo_deporte);


--
-- Name: idx_canchas_tipo_cancha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_tipo_cancha ON public.canchas USING btree (tipo_cancha_id);


--
-- Name: idx_clientes_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_email ON public.clientes USING btree (email);


--
-- Name: idx_clientes_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_estado ON public.clientes USING btree (estado);


--
-- Name: idx_pagos_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_cliente ON public.pagos USING btree (cliente_id);


--
-- Name: idx_pagos_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_estado ON public.pagos USING btree (estado);


--
-- Name: idx_pagos_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_fecha ON public.pagos USING btree (fecha_pago);


--
-- Name: idx_pagos_reserva; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_reserva ON public.pagos USING btree (reserva_id);


--
-- Name: idx_reservas_cancha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_cancha ON public.reservas USING btree (cancha_id);


--
-- Name: idx_reservas_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_cliente ON public.reservas USING btree (cliente_id);


--
-- Name: idx_reservas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_estado ON public.reservas USING btree (estado);


--
-- Name: idx_reservas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_fecha ON public.reservas USING btree (fecha_reserva);


--
-- Name: tipos_cancha trigger_actualizar_fecha_tipos_cancha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_actualizar_fecha_tipos_cancha BEFORE UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.actualizar_fecha_tipos_cancha();


--
-- Name: canchas trigger_auditoria_canchas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_canchas AFTER INSERT OR DELETE OR UPDATE ON public.canchas FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- Name: clientes trigger_auditoria_clientes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_clientes AFTER INSERT OR DELETE OR UPDATE ON public.clientes FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- Name: reservas trigger_auditoria_reservas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_reservas AFTER INSERT OR DELETE OR UPDATE ON public.reservas FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- Name: tipos_cancha trigger_auditoria_tipos_cancha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_tipos_cancha AFTER INSERT OR DELETE OR UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- Name: usuarios trigger_auditoria_usuarios; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_usuarios AFTER INSERT OR DELETE OR UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- Name: canchas update_canchas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_canchas_updated_at BEFORE UPDATE ON public.canchas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: clientes update_clientes_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON public.clientes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: pagos update_pagos_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_pagos_updated_at BEFORE UPDATE ON public.pagos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: reservas update_reservas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON public.reservas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: tipos_cancha update_tipos_cancha_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_tipos_cancha_updated_at BEFORE UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: usuarios update_usuarios_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: auditoria auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: canchas canchas_tipo_cancha_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas
    ADD CONSTRAINT canchas_tipo_cancha_id_fkey FOREIGN KEY (tipo_cancha_id) REFERENCES public.tipos_cancha(id);


--
-- Name: pagos pagos_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: pagos pagos_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id);


--
-- Name: reservas reservas_cancha_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_cancha_id_fkey FOREIGN KEY (cancha_id) REFERENCES public.canchas(id);


--
-- Name: reservas reservas_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO operador_reservas;
GRANT USAGE ON SCHEMA public TO consultor_reservas;


--
-- Name: FUNCTION actualizar_fecha_tipos_cancha(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.actualizar_fecha_tipos_cancha() TO admin_reservas;


--
-- Name: PROCEDURE proc_generar_estadisticas(IN p_fecha_inicio date, IN p_fecha_fin date, IN p_tipo_reporte character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON PROCEDURE public.proc_generar_estadisticas(IN p_fecha_inicio date, IN p_fecha_fin date, IN p_tipo_reporte character varying) TO admin_reservas;
GRANT ALL ON PROCEDURE public.proc_generar_estadisticas(IN p_fecha_inicio date, IN p_fecha_fin date, IN p_tipo_reporte character varying) TO operador_reservas;


--
-- Name: PROCEDURE proc_gestionar_reserva(IN p_accion character varying, IN p_id integer, IN p_cliente_id integer, IN p_cancha_id integer, IN p_fecha_reserva date, IN p_hora_inicio time without time zone, IN p_hora_fin time without time zone, IN p_observaciones text, IN p_estado character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON PROCEDURE public.proc_gestionar_reserva(IN p_accion character varying, IN p_id integer, IN p_cliente_id integer, IN p_cancha_id integer, IN p_fecha_reserva date, IN p_hora_inicio time without time zone, IN p_hora_fin time without time zone, IN p_observaciones text, IN p_estado character varying) TO admin_reservas;
GRANT ALL ON PROCEDURE public.proc_gestionar_reserva(IN p_accion character varying, IN p_id integer, IN p_cliente_id integer, IN p_cancha_id integer, IN p_fecha_reserva date, IN p_hora_inicio time without time zone, IN p_hora_fin time without time zone, IN p_observaciones text, IN p_estado character varying) TO operador_reservas;


--
-- Name: PROCEDURE proc_registrar_auditoria_manual(IN p_usuario_id integer, IN p_tipo_accion character varying, IN p_tabla character varying, IN p_registro_id integer, IN p_detalles text, IN p_ip_address character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON PROCEDURE public.proc_registrar_auditoria_manual(IN p_usuario_id integer, IN p_tipo_accion character varying, IN p_tabla character varying, IN p_registro_id integer, IN p_detalles text, IN p_ip_address character varying) TO admin_reservas;
GRANT ALL ON PROCEDURE public.proc_registrar_auditoria_manual(IN p_usuario_id integer, IN p_tipo_accion character varying, IN p_tabla character varying, IN p_registro_id integer, IN p_detalles text, IN p_ip_address character varying) TO operador_reservas;


--
-- Name: PROCEDURE proc_registrar_pago(IN p_reserva_id integer, IN p_monto numeric, IN p_metodo_pago character varying, IN p_observaciones text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON PROCEDURE public.proc_registrar_pago(IN p_reserva_id integer, IN p_monto numeric, IN p_metodo_pago character varying, IN p_observaciones text) TO admin_reservas;
GRANT ALL ON PROCEDURE public.proc_registrar_pago(IN p_reserva_id integer, IN p_monto numeric, IN p_metodo_pago character varying, IN p_observaciones text) TO operador_reservas;


--
-- Name: PROCEDURE proc_validar_y_limpiar_datos(IN p_tabla character varying, IN p_accion character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON PROCEDURE public.proc_validar_y_limpiar_datos(IN p_tabla character varying, IN p_accion character varying) TO admin_reservas;


--
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_updated_at_column() TO admin_reservas;


--
-- Name: TABLE auditoria; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.auditoria TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.auditoria TO operador_reservas;
GRANT SELECT ON TABLE public.auditoria TO consultor_reservas;


--
-- Name: SEQUENCE auditoria_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.auditoria_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.auditoria_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.auditoria_id_seq TO consultor_reservas;


--
-- Name: TABLE canchas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.canchas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.canchas TO operador_reservas;
GRANT SELECT ON TABLE public.canchas TO consultor_reservas;


--
-- Name: SEQUENCE canchas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.canchas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.canchas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.canchas_id_seq TO consultor_reservas;


--
-- Name: TABLE clientes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clientes TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clientes TO operador_reservas;
GRANT SELECT ON TABLE public.clientes TO consultor_reservas;


--
-- Name: SEQUENCE clientes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clientes_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.clientes_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.clientes_id_seq TO consultor_reservas;


--
-- Name: TABLE pagos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pagos TO operador_reservas;
GRANT SELECT ON TABLE public.pagos TO consultor_reservas;


--
-- Name: SEQUENCE pagos_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.pagos_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.pagos_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.pagos_id_seq TO consultor_reservas;


--
-- Name: TABLE reservas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.reservas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.reservas TO operador_reservas;
GRANT SELECT ON TABLE public.reservas TO consultor_reservas;


--
-- Name: SEQUENCE reservas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.reservas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.reservas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.reservas_id_seq TO consultor_reservas;


--
-- Name: TABLE tipos_cancha; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tipos_cancha TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.tipos_cancha TO operador_reservas;
GRANT SELECT ON TABLE public.tipos_cancha TO consultor_reservas;


--
-- Name: SEQUENCE tipos_cancha_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.tipos_cancha_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.tipos_cancha_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.tipos_cancha_id_seq TO consultor_reservas;


--
-- Name: TABLE usuarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.usuarios TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.usuarios TO operador_reservas;
GRANT SELECT ON TABLE public.usuarios TO consultor_reservas;


--
-- Name: SEQUENCE usuarios_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.usuarios_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.usuarios_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.usuarios_id_seq TO consultor_reservas;


--
-- Name: TABLE vista_canchas_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_canchas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_completa TO consultor_reservas;


--
-- Name: TABLE vista_canchas_disponibles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_canchas_disponibles TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_disponibles TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_disponibles TO consultor_reservas;


--
-- Name: TABLE vista_canchas_mas_recaudan; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_canchas_mas_recaudan TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_mas_recaudan TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_mas_recaudan TO consultor_reservas;


--
-- Name: TABLE vista_canchas_mas_usadas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_canchas_mas_usadas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_mas_usadas TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_mas_usadas TO consultor_reservas;


--
-- Name: TABLE vista_clientes_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_clientes_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_clientes_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_clientes_completa TO consultor_reservas;


--
-- Name: TABLE vista_historial_pagos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_historial_pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_historial_pagos TO operador_reservas;
GRANT SELECT ON TABLE public.vista_historial_pagos TO consultor_reservas;


--
-- Name: TABLE vista_pagos_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_pagos_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_pagos_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_pagos_completa TO consultor_reservas;


--
-- Name: TABLE vista_pagos_pendientes_cliente; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_pagos_pendientes_cliente TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_pagos_pendientes_cliente TO operador_reservas;
GRANT SELECT ON TABLE public.vista_pagos_pendientes_cliente TO consultor_reservas;


--
-- Name: TABLE vista_reporte_ingresos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_reporte_ingresos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reporte_ingresos TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reporte_ingresos TO consultor_reservas;


--
-- Name: TABLE vista_reporte_reservas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_reporte_reservas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reporte_reservas TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reporte_reservas TO consultor_reservas;


--
-- Name: TABLE vista_reservas_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_reservas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_completa TO consultor_reservas;


--
-- Name: TABLE vista_reservas_con_pagos; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_reservas_con_pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_con_pagos TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_con_pagos TO consultor_reservas;


--
-- Name: TABLE vista_reservas_pendientes_pago; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_reservas_pendientes_pago TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_pendientes_pago TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_pendientes_pago TO consultor_reservas;


--
-- Name: TABLE vista_resumen_pagos_periodo; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vista_resumen_pagos_periodo TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_resumen_pagos_periodo TO operador_reservas;
GRANT SELECT ON TABLE public.vista_resumen_pagos_periodo TO consultor_reservas;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON SEQUENCES TO consultor_reservas;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: root123
--

ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT ON SEQUENCES TO consultor_reservas;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO consultor_reservas;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: root123
--

ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT ALL ON TABLES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT ON TABLES TO consultor_reservas;


--
-- PostgreSQL database dump complete
--

