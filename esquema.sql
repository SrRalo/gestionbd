--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-08-03 15:46:11

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
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5067 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 239 (class 1255 OID 26644)
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
-- TOC entry 237 (class 1255 OID 26508)
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
-- TOC entry 242 (class 1255 OID 26641)
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
-- TOC entry 258 (class 1255 OID 26649)
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
-- TOC entry 241 (class 1255 OID 26647)
-- Name: crear_tipo_cancha(character varying, text, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- TOC entry 240 (class 1255 OID 26645)
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
-- TOC entry 238 (class 1255 OID 26643)
-- Name: obtener_cancha_por_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- TOC entry 255 (class 1255 OID 26642)
-- Name: obtener_canchas(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- TOC entry 254 (class 1255 OID 26646)
-- Name: obtener_canchas_con_tipos(); Type: FUNCTION; Schema: public; Owner: postgres
--

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

--
-- TOC entry 256 (class 1255 OID 26648)
-- Name: obtener_tipos_cancha(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_tipos_cancha() RETURNS TABLE(id integer, nombre character varying, descripcion text, precio_por_hora numeric, activo boolean, created_at timestamp without time zone, updated_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT tc.id, tc.nombre, tc.descripcion, tc.precio_por_hora, 
           tc.activo, tc.created_at, tc.updated_at
    FROM tipos_cancha tc
    ORDER BY tc.nombre;
END;
$$;


ALTER FUNCTION public.obtener_tipos_cancha() OWNER TO postgres;

--
-- TOC entry 257 (class 1255 OID 26651)
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
-- TOC entry 236 (class 1255 OID 26473)
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
-- TOC entry 259 (class 1255 OID 26650)
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
-- TOC entry 228 (class 1259 OID 26442)
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
-- TOC entry 227 (class 1259 OID 26441)
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
-- TOC entry 5072 (class 0 OID 0)
-- Dependencies: 227
-- Name: auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditoria_id_seq OWNED BY public.auditoria.id;


--
-- TOC entry 222 (class 1259 OID 26383)
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
-- TOC entry 221 (class 1259 OID 26382)
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
-- TOC entry 5075 (class 0 OID 0)
-- Dependencies: 221
-- Name: canchas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.canchas_id_seq OWNED BY public.canchas.id;


--
-- TOC entry 220 (class 1259 OID 26369)
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
-- TOC entry 219 (class 1259 OID 26368)
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
-- TOC entry 5078 (class 0 OID 0)
-- Dependencies: 219
-- Name: clientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clientes_id_seq OWNED BY public.clientes.id;


--
-- TOC entry 226 (class 1259 OID 26420)
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
-- TOC entry 225 (class 1259 OID 26419)
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
-- TOC entry 5081 (class 0 OID 0)
-- Dependencies: 225
-- Name: pagos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pagos_id_seq OWNED BY public.pagos.id;


--
-- TOC entry 224 (class 1259 OID 26398)
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
-- TOC entry 223 (class 1259 OID 26397)
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
-- TOC entry 5084 (class 0 OID 0)
-- Dependencies: 223
-- Name: reservas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservas_id_seq OWNED BY public.reservas.id;


--
-- TOC entry 230 (class 1259 OID 26490)
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
-- TOC entry 229 (class 1259 OID 26489)
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
-- TOC entry 5087 (class 0 OID 0)
-- Dependencies: 229
-- Name: tipos_cancha_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipos_cancha_id_seq OWNED BY public.tipos_cancha.id;


--
-- TOC entry 218 (class 1259 OID 26352)
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
-- TOC entry 217 (class 1259 OID 26351)
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
-- TOC entry 5090 (class 0 OID 0)
-- Dependencies: 217
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- TOC entry 232 (class 1259 OID 26603)
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
-- TOC entry 231 (class 1259 OID 26598)
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
-- TOC entry 234 (class 1259 OID 26628)
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
-- TOC entry 233 (class 1259 OID 26623)
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
-- TOC entry 235 (class 1259 OID 26633)
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
-- TOC entry 4833 (class 2604 OID 26445)
-- Name: auditoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria ALTER COLUMN id SET DEFAULT nextval('public.auditoria_id_seq'::regclass);


--
-- TOC entry 4818 (class 2604 OID 26386)
-- Name: canchas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas ALTER COLUMN id SET DEFAULT nextval('public.canchas_id_seq'::regclass);


--
-- TOC entry 4814 (class 2604 OID 26372)
-- Name: clientes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);


--
-- TOC entry 4829 (class 2604 OID 26423)
-- Name: pagos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos ALTER COLUMN id SET DEFAULT nextval('public.pagos_id_seq'::regclass);


--
-- TOC entry 4825 (class 2604 OID 26401)
-- Name: reservas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id SET DEFAULT nextval('public.reservas_id_seq'::regclass);


--
-- TOC entry 4836 (class 2604 OID 26493)
-- Name: tipos_cancha id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha ALTER COLUMN id SET DEFAULT nextval('public.tipos_cancha_id_seq'::regclass);


--
-- TOC entry 4809 (class 2604 OID 26355)
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- TOC entry 5059 (class 0 OID 26442)
-- Dependencies: 228
-- Data for Name: auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria (id, usuario_id, tipo_accion, tabla, registro_id, detalles, resultado, ip_address, fecha_hora) FROM stdin;
1	\N	DELETE	canchas	6	Registro eliminado	SUCCESS	127.0.0.1	2025-08-02 19:27:57.898328
\.


--
-- TOC entry 5053 (class 0 OID 26383)
-- Dependencies: 222
-- Data for Name: canchas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.canchas (id, nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion, fecha_creacion, fecha_actualizacion, tipo_cancha_id) FROM stdin;
2	Cancha 2 - Fútbol	Fútbol	100	50.00	Activa	06:00:00	22:00:00	Cancha de fútbol 11 con césped sintético	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
3	Cancha 3 - Basketball	Basketball	50	40.00	Activa	06:00:00	22:00:00	Cancha de basketball con piso de madera	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
4	Cancha 4 - Tennis	Tennis	30	60.00	Activa	06:00:00	22:00:00	Cancha de tennis con superficie de arcilla	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
5	Cancha 5 - Voleibol	Voleibol	40	35.00	Activa	06:00:00	22:00:00	Cancha de voleibol de arena	2025-07-31 11:20:41.988297	2025-07-31 11:38:53.28448	1
7	prueba 2	Fútbol	50	50.00	Activa	06:00:00	22:00:00	prueba operador	2025-08-01 16:56:27.162001	2025-08-01 16:56:27.162001	15
1	Cancha Elefante	Fútbol	100	50.00	Activa	06:00:00	22:00:00	Cancha de fútbol 11 con césped sintético	2025-07-31 11:20:41.988297	2025-08-01 17:07:43.665966	1
\.


--
-- TOC entry 5051 (class 0 OID 26369)
-- Dependencies: 220
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
-- TOC entry 5057 (class 0 OID 26420)
-- Dependencies: 226
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pagos (id, reserva_id, cliente_id, monto, metodo_pago, estado, fecha_pago, observaciones, fecha_creacion, fecha_actualizacion) FROM stdin;
1	1	1	100.00	Efectivo	Completado	2025-07-31	Pago en efectivo	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
2	3	3	60.00	Tarjeta de Crédito	Completado	2025-07-31	Pago con tarjeta	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
3	5	5	100.00	Transferencia	Completado	2025-07-31	Transferencia bancaria	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
\.


--
-- TOC entry 5055 (class 0 OID 26398)
-- Dependencies: 224
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservas (id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, duracion, estado, observaciones, fecha_creacion, fecha_actualizacion) FROM stdin;
1	1	1	2025-08-01	14:00:00	16:00:00	2.00	Confirmada	Partido de fútbol	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
2	2	3	2025-08-02	16:00:00	18:00:00	2.00	Pendiente	Entrenamiento de basketball	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
3	3	4	2025-08-03	10:00:00	11:00:00	1.00	Confirmada	Clase de tennis	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
4	4	5	2025-08-01	18:00:00	20:00:00	2.00	Pendiente	Torneo de voleibol	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
5	5	2	2025-08-04	20:00:00	22:00:00	2.00	Confirmada	Partido nocturno	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
8	4	2	2025-08-02	14:00:00	16:00:00	2.00	pendiente	\N	2025-08-02 19:07:35.906714	2025-08-02 19:07:35.906714
9	2	7	2025-08-02	14:00:00	18:00:00	4.00	pendiente	\N	2025-08-02 19:07:52.007044	2025-08-02 19:07:52.007044
\.


--
-- TOC entry 5061 (class 0 OID 26490)
-- Dependencies: 230
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
\.


--
-- TOC entry 5049 (class 0 OID 26352)
-- Dependencies: 218
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, email, password, nombre, apellido, rol, estado, telefono, fecha_creacion, fecha_actualizacion) FROM stdin;
1	admin	admin@sportcourt.com	8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918	Administrador	Sistema	admin_reservas	Activo	\N	2025-07-31 11:20:41.988297	2025-07-31 11:20:41.988297
\.


--
-- TOC entry 5097 (class 0 OID 0)
-- Dependencies: 227
-- Name: auditoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditoria_id_seq', 1, true);


--
-- TOC entry 5098 (class 0 OID 0)
-- Dependencies: 221
-- Name: canchas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.canchas_id_seq', 8, true);


--
-- TOC entry 5099 (class 0 OID 0)
-- Dependencies: 219
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clientes_id_seq', 5, true);


--
-- TOC entry 5100 (class 0 OID 0)
-- Dependencies: 225
-- Name: pagos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pagos_id_seq', 3, true);


--
-- TOC entry 5101 (class 0 OID 0)
-- Dependencies: 223
-- Name: reservas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservas_id_seq', 9, true);


--
-- TOC entry 5102 (class 0 OID 0)
-- Dependencies: 229
-- Name: tipos_cancha_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipos_cancha_id_seq', 31, true);


--
-- TOC entry 5103 (class 0 OID 0)
-- Dependencies: 217
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);


--
-- TOC entry 4871 (class 2606 OID 26451)
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id);


--
-- TOC entry 4854 (class 2606 OID 26396)
-- Name: canchas canchas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas
    ADD CONSTRAINT canchas_pkey PRIMARY KEY (id);


--
-- TOC entry 4848 (class 2606 OID 26381)
-- Name: clientes clientes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_email_key UNIQUE (email);


--
-- TOC entry 4850 (class 2606 OID 26379)
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- TOC entry 4869 (class 2606 OID 26430)
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (id);


--
-- TOC entry 4863 (class 2606 OID 26408)
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id);


--
-- TOC entry 4877 (class 2606 OID 26514)
-- Name: tipos_cancha tipos_cancha_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha
    ADD CONSTRAINT tipos_cancha_nombre_key UNIQUE (nombre);


--
-- TOC entry 4879 (class 2606 OID 26501)
-- Name: tipos_cancha tipos_cancha_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_cancha
    ADD CONSTRAINT tipos_cancha_pkey PRIMARY KEY (id);


--
-- TOC entry 4842 (class 2606 OID 26367)
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- TOC entry 4844 (class 2606 OID 26363)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 4846 (class 2606 OID 26365)
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- TOC entry 4872 (class 1259 OID 26466)
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_fecha ON public.auditoria USING btree (fecha_hora);


--
-- TOC entry 4873 (class 1259 OID 26468)
-- Name: idx_auditoria_tabla; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_tabla ON public.auditoria USING btree (tabla);


--
-- TOC entry 4874 (class 1259 OID 26467)
-- Name: idx_auditoria_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_tipo ON public.auditoria USING btree (tipo_accion);


--
-- TOC entry 4875 (class 1259 OID 26465)
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario ON public.auditoria USING btree (usuario_id);


--
-- TOC entry 4855 (class 1259 OID 26471)
-- Name: idx_canchas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_estado ON public.canchas USING btree (estado);


--
-- TOC entry 4856 (class 1259 OID 26472)
-- Name: idx_canchas_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_tipo ON public.canchas USING btree (tipo_deporte);


--
-- TOC entry 4857 (class 1259 OID 26507)
-- Name: idx_canchas_tipo_cancha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_canchas_tipo_cancha ON public.canchas USING btree (tipo_cancha_id);


--
-- TOC entry 4851 (class 1259 OID 26469)
-- Name: idx_clientes_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_email ON public.clientes USING btree (email);


--
-- TOC entry 4852 (class 1259 OID 26470)
-- Name: idx_clientes_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_estado ON public.clientes USING btree (estado);


--
-- TOC entry 4864 (class 1259 OID 26462)
-- Name: idx_pagos_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_cliente ON public.pagos USING btree (cliente_id);


--
-- TOC entry 4865 (class 1259 OID 26464)
-- Name: idx_pagos_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_estado ON public.pagos USING btree (estado);


--
-- TOC entry 4866 (class 1259 OID 26463)
-- Name: idx_pagos_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_fecha ON public.pagos USING btree (fecha_pago);


--
-- TOC entry 4867 (class 1259 OID 26461)
-- Name: idx_pagos_reserva; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_reserva ON public.pagos USING btree (reserva_id);


--
-- TOC entry 4858 (class 1259 OID 26459)
-- Name: idx_reservas_cancha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_cancha ON public.reservas USING btree (cancha_id);


--
-- TOC entry 4859 (class 1259 OID 26458)
-- Name: idx_reservas_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_cliente ON public.reservas USING btree (cliente_id);


--
-- TOC entry 4860 (class 1259 OID 26460)
-- Name: idx_reservas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_estado ON public.reservas USING btree (estado);


--
-- TOC entry 4861 (class 1259 OID 26457)
-- Name: idx_reservas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservas_fecha ON public.reservas USING btree (fecha_reserva);


--
-- TOC entry 4895 (class 2620 OID 26510)
-- Name: tipos_cancha trigger_actualizar_fecha_tipos_cancha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_actualizar_fecha_tipos_cancha BEFORE UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.actualizar_fecha_tipos_cancha();


--
-- TOC entry 4890 (class 2620 OID 26652)
-- Name: canchas trigger_auditoria_canchas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_canchas AFTER INSERT OR DELETE OR UPDATE ON public.canchas FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- TOC entry 4888 (class 2620 OID 26654)
-- Name: clientes trigger_auditoria_clientes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_clientes AFTER INSERT OR DELETE OR UPDATE ON public.clientes FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- TOC entry 4892 (class 2620 OID 26653)
-- Name: reservas trigger_auditoria_reservas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_reservas AFTER INSERT OR DELETE OR UPDATE ON public.reservas FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- TOC entry 4896 (class 2620 OID 26656)
-- Name: tipos_cancha trigger_auditoria_tipos_cancha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_tipos_cancha AFTER INSERT OR DELETE OR UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- TOC entry 4886 (class 2620 OID 26655)
-- Name: usuarios trigger_auditoria_usuarios; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_auditoria_usuarios AFTER INSERT OR DELETE OR UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_automatica();


--
-- TOC entry 4891 (class 2620 OID 26476)
-- Name: canchas update_canchas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_canchas_updated_at BEFORE UPDATE ON public.canchas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4889 (class 2620 OID 26475)
-- Name: clientes update_clientes_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON public.clientes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4894 (class 2620 OID 26478)
-- Name: pagos update_pagos_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_pagos_updated_at BEFORE UPDATE ON public.pagos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4893 (class 2620 OID 26477)
-- Name: reservas update_reservas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON public.reservas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4897 (class 2620 OID 26517)
-- Name: tipos_cancha update_tipos_cancha_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_tipos_cancha_updated_at BEFORE UPDATE ON public.tipos_cancha FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4887 (class 2620 OID 26474)
-- Name: usuarios update_usuarios_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4885 (class 2606 OID 26452)
-- Name: auditoria auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- TOC entry 4880 (class 2606 OID 26502)
-- Name: canchas canchas_tipo_cancha_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canchas
    ADD CONSTRAINT canchas_tipo_cancha_id_fkey FOREIGN KEY (tipo_cancha_id) REFERENCES public.tipos_cancha(id);


--
-- TOC entry 4883 (class 2606 OID 26436)
-- Name: pagos pagos_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- TOC entry 4884 (class 2606 OID 26431)
-- Name: pagos pagos_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id);


--
-- TOC entry 4881 (class 2606 OID 26414)
-- Name: reservas reservas_cancha_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_cancha_id_fkey FOREIGN KEY (cancha_id) REFERENCES public.canchas(id);


--
-- TOC entry 4882 (class 2606 OID 26409)
-- Name: reservas reservas_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- TOC entry 5068 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO operador_reservas;
GRANT USAGE ON SCHEMA public TO consultor_reservas;


--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 237
-- Name: FUNCTION actualizar_fecha_tipos_cancha(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.actualizar_fecha_tipos_cancha() TO admin_reservas;


--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 236
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_updated_at_column() TO admin_reservas;


--
-- TOC entry 5071 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE auditoria; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.auditoria TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.auditoria TO operador_reservas;
GRANT SELECT ON TABLE public.auditoria TO consultor_reservas;


--
-- TOC entry 5073 (class 0 OID 0)
-- Dependencies: 227
-- Name: SEQUENCE auditoria_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.auditoria_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.auditoria_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.auditoria_id_seq TO consultor_reservas;


--
-- TOC entry 5074 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE canchas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.canchas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.canchas TO operador_reservas;
GRANT SELECT ON TABLE public.canchas TO consultor_reservas;


--
-- TOC entry 5076 (class 0 OID 0)
-- Dependencies: 221
-- Name: SEQUENCE canchas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.canchas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.canchas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.canchas_id_seq TO consultor_reservas;


--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE clientes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clientes TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clientes TO operador_reservas;
GRANT SELECT ON TABLE public.clientes TO consultor_reservas;


--
-- TOC entry 5079 (class 0 OID 0)
-- Dependencies: 219
-- Name: SEQUENCE clientes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clientes_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.clientes_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.clientes_id_seq TO consultor_reservas;


--
-- TOC entry 5080 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE pagos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pagos TO operador_reservas;
GRANT SELECT ON TABLE public.pagos TO consultor_reservas;


--
-- TOC entry 5082 (class 0 OID 0)
-- Dependencies: 225
-- Name: SEQUENCE pagos_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.pagos_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.pagos_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.pagos_id_seq TO consultor_reservas;


--
-- TOC entry 5083 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE reservas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.reservas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.reservas TO operador_reservas;
GRANT SELECT ON TABLE public.reservas TO consultor_reservas;


--
-- TOC entry 5085 (class 0 OID 0)
-- Dependencies: 223
-- Name: SEQUENCE reservas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.reservas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.reservas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.reservas_id_seq TO consultor_reservas;


--
-- TOC entry 5086 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE tipos_cancha; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tipos_cancha TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.tipos_cancha TO operador_reservas;
GRANT SELECT ON TABLE public.tipos_cancha TO consultor_reservas;


--
-- TOC entry 5088 (class 0 OID 0)
-- Dependencies: 229
-- Name: SEQUENCE tipos_cancha_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.tipos_cancha_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.tipos_cancha_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.tipos_cancha_id_seq TO consultor_reservas;


--
-- TOC entry 5089 (class 0 OID 0)
-- Dependencies: 218
-- Name: TABLE usuarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.usuarios TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.usuarios TO operador_reservas;
GRANT SELECT ON TABLE public.usuarios TO consultor_reservas;


--
-- TOC entry 5091 (class 0 OID 0)
-- Dependencies: 217
-- Name: SEQUENCE usuarios_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.usuarios_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.usuarios_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.usuarios_id_seq TO consultor_reservas;


--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE vista_canchas_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_canchas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_canchas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_canchas_completa TO consultor_reservas;


--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE vista_clientes_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_clientes_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_clientes_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_clientes_completa TO consultor_reservas;


--
-- TOC entry 5094 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE vista_pagos_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_pagos_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_pagos_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_pagos_completa TO consultor_reservas;


--
-- TOC entry 5095 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE vista_reservas_completa; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_reservas_completa TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_completa TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_completa TO consultor_reservas;


--
-- TOC entry 5096 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE vista_reservas_con_pagos; Type: ACL; Schema: public; Owner: root123
--

GRANT ALL ON TABLE public.vista_reservas_con_pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vista_reservas_con_pagos TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_con_pagos TO consultor_reservas;


--
-- TOC entry 2108 (class 826 OID 26516)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON SEQUENCES TO consultor_reservas;


--
-- TOC entry 2110 (class 826 OID 26519)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: root123
--

ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT ON SEQUENCES TO consultor_reservas;


--
-- TOC entry 2107 (class 826 OID 26515)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO consultor_reservas;


--
-- TOC entry 2109 (class 826 OID 26518)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: root123
--

ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT ALL ON TABLES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE root123 IN SCHEMA public GRANT SELECT ON TABLES TO consultor_reservas;


-- Completed on 2025-08-03 15:46:12

--
-- PostgreSQL database dump complete
--

