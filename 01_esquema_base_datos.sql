-- =====================================================
-- ESQUEMA DE BASE DE DATOS - SPORTCOURT RESERVATIONS
-- =====================================================
-- Archivo: 01_esquema_base_datos.sql
-- Descripción: Contiene solo el esquema de la base de datos
-- Fecha: 2025-08-03
-- =====================================================

-- =====================================================
-- CREACIÓN DE ROLES
-- =====================================================

-- Crear rol de administrador
CREATE ROLE admin_reservas WITH
    LOGIN
    PASSWORD 'admin123'
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

-- Crear rol de operador
CREATE ROLE operador_reservas WITH
    LOGIN
    PASSWORD 'operador123'
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

-- Crear rol de consultor
CREATE ROLE consultor_reservas WITH
    LOGIN
    PASSWORD 'consultor123'
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;


-- =====================================================
-- SECUENCIAS
-- =====================================================

-- Secuencia para auditoria
CREATE SEQUENCE public.auditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.auditoria_id_seq OWNER TO postgres;

-- Secuencia para canchas
CREATE SEQUENCE public.canchas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.canchas_id_seq OWNER TO postgres;

-- Secuencia para clientes
CREATE SEQUENCE public.clientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.clientes_id_seq OWNER TO postgres;

-- Secuencia para pagos
CREATE SEQUENCE public.pagos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.pagos_id_seq OWNER TO postgres;

-- Secuencia para reservas
CREATE SEQUENCE public.reservas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.reservas_id_seq OWNER TO postgres;

-- Secuencia para tipos_cancha
CREATE SEQUENCE public.tipos_cancha_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.tipos_cancha_id_seq OWNER TO postgres;

-- Secuencia para usuarios
CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

-- =====================================================
-- TABLAS
-- =====================================================

-- Tabla auditoria
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

-- Tabla canchas
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

-- Tabla clientes
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

-- Tabla pagos
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

-- Tabla reservas
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

-- Tabla tipos_cancha
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

-- Tabla usuarios
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

-- =====================================================
-- VALORES POR DEFECTO
-- =====================================================

-- Configurar valores por defecto para IDs
ALTER TABLE ONLY public.auditoria ALTER COLUMN id SET DEFAULT nextval('public.auditoria_id_seq'::regclass);
ALTER TABLE ONLY public.canchas ALTER COLUMN id SET DEFAULT nextval('public.canchas_id_seq'::regclass);
ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);
ALTER TABLE ONLY public.pagos ALTER COLUMN id SET DEFAULT nextval('public.pagos_id_seq'::regclass);
ALTER TABLE ONLY public.reservas ALTER COLUMN id SET DEFAULT nextval('public.reservas_id_seq'::regclass);
ALTER TABLE ONLY public.tipos_cancha ALTER COLUMN id SET DEFAULT nextval('public.tipos_cancha_id_seq'::regclass);
ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);

-- =====================================================
-- RESTRICCIONES (CONSTRAINTS)
-- =====================================================

-- Claves primarias
ALTER TABLE ONLY public.auditoria ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.canchas ADD CONSTRAINT canchas_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.clientes ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.pagos ADD CONSTRAINT pagos_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.reservas ADD CONSTRAINT reservas_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.tipos_cancha ADD CONSTRAINT tipos_cancha_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.usuarios ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);

-- Claves únicas
ALTER TABLE ONLY public.clientes ADD CONSTRAINT clientes_email_key UNIQUE (email);
ALTER TABLE ONLY public.tipos_cancha ADD CONSTRAINT tipos_cancha_nombre_key UNIQUE (nombre);
ALTER TABLE ONLY public.usuarios ADD CONSTRAINT usuarios_email_key UNIQUE (email);
ALTER TABLE ONLY public.usuarios ADD CONSTRAINT usuarios_username_key UNIQUE (username);

-- Claves foráneas
ALTER TABLE ONLY public.auditoria ADD CONSTRAINT auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);
ALTER TABLE ONLY public.canchas ADD CONSTRAINT canchas_tipo_cancha_id_fkey FOREIGN KEY (tipo_cancha_id) REFERENCES public.tipos_cancha(id);
ALTER TABLE ONLY public.pagos ADD CONSTRAINT pagos_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);
ALTER TABLE ONLY public.pagos ADD CONSTRAINT pagos_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id);
ALTER TABLE ONLY public.reservas ADD CONSTRAINT reservas_cancha_id_fkey FOREIGN KEY (cancha_id) REFERENCES public.canchas(id);
ALTER TABLE ONLY public.reservas ADD CONSTRAINT reservas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);

-- =====================================================
-- ÍNDICES
-- =====================================================

-- Índices para auditoria
CREATE INDEX idx_auditoria_fecha ON public.auditoria USING btree (fecha_hora);
CREATE INDEX idx_auditoria_tabla ON public.auditoria USING btree (tabla);
CREATE INDEX idx_auditoria_tipo ON public.auditoria USING btree (tipo_accion);
CREATE INDEX idx_auditoria_usuario ON public.auditoria USING btree (usuario_id);

-- Índices para canchas
CREATE INDEX idx_canchas_estado ON public.canchas USING btree (estado);
CREATE INDEX idx_canchas_tipo ON public.canchas USING btree (tipo_deporte);
CREATE INDEX idx_canchas_tipo_cancha ON public.canchas USING btree (tipo_cancha_id);

-- Índices para clientes
CREATE INDEX idx_clientes_email ON public.clientes USING btree (email);
CREATE INDEX idx_clientes_estado ON public.clientes USING btree (estado);

-- Índices para pagos
CREATE INDEX idx_pagos_cliente ON public.pagos USING btree (cliente_id);
CREATE INDEX idx_pagos_estado ON public.pagos USING btree (estado);
CREATE INDEX idx_pagos_fecha ON public.pagos USING btree (fecha_pago);
CREATE INDEX idx_pagos_reserva ON public.pagos USING btree (reserva_id);

-- Índices para reservas
CREATE INDEX idx_reservas_cancha ON public.reservas USING btree (cancha_id);
CREATE INDEX idx_reservas_cliente ON public.reservas USING btree (cliente_id);
CREATE INDEX idx_reservas_estado ON public.reservas USING btree (estado);
CREATE INDEX idx_reservas_fecha ON public.reservas USING btree (fecha_reserva);

-- =====================================================
-- ROLES Y PERMISOS
-- =====================================================

-- Otorgar permisos al esquema
GRANT USAGE ON SCHEMA public TO operador_reservas;
GRANT USAGE ON SCHEMA public TO consultor_reservas;

-- Permisos para tablas
GRANT ALL ON TABLE public.auditoria TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.auditoria TO operador_reservas;
GRANT SELECT ON TABLE public.auditoria TO consultor_reservas;

GRANT ALL ON TABLE public.canchas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.canchas TO operador_reservas;
GRANT SELECT ON TABLE public.canchas TO consultor_reservas;

GRANT ALL ON TABLE public.clientes TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clientes TO operador_reservas;
GRANT SELECT ON TABLE public.clientes TO consultor_reservas;

GRANT ALL ON TABLE public.pagos TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.pagos TO operador_reservas;
GRANT SELECT ON TABLE public.pagos TO consultor_reservas;

GRANT ALL ON TABLE public.reservas TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.reservas TO operador_reservas;
GRANT SELECT ON TABLE public.reservas TO consultor_reservas;

GRANT ALL ON TABLE public.tipos_cancha TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.tipos_cancha TO operador_reservas;
GRANT SELECT ON TABLE public.tipos_cancha TO consultor_reservas;

GRANT ALL ON TABLE public.usuarios TO admin_reservas;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.usuarios TO operador_reservas;
GRANT SELECT ON TABLE public.usuarios TO consultor_reservas;

-- Permisos para secuencias
GRANT ALL ON SEQUENCE public.auditoria_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.auditoria_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.auditoria_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.canchas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.canchas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.canchas_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.clientes_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.clientes_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.clientes_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.pagos_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.pagos_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.pagos_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.reservas_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.reservas_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.reservas_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.tipos_cancha_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.tipos_cancha_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.tipos_cancha_id_seq TO consultor_reservas;

GRANT ALL ON SEQUENCE public.usuarios_id_seq TO admin_reservas;
GRANT SELECT,USAGE ON SEQUENCE public.usuarios_id_seq TO operador_reservas;
GRANT SELECT ON SEQUENCE public.usuarios_id_seq TO consultor_reservas;

-- Permisos por defecto para futuros objetos
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO consultor_reservas;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO operador_reservas;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON SEQUENCES TO consultor_reservas;

-- =====================================================
-- ESQUEMA COMPLETADO
-- ===================================================== 