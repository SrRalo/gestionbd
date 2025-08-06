-- =====================================================
-- DATOS E INSERTS - SPORTCOURT RESERVATIONS
-- =====================================================
-- Archivo: 03_datos_inserts.sql
-- Descripción: Contiene todos los inserts de datos de las tablas
-- Fecha: 2025-08-03
-- =====================================================

-- =====================================================
-- CONFIGURACIÓN DE SECUENCIAS
-- =====================================================

-- Configurar valores de secuencias
SELECT pg_catalog.setval('public.auditoria_id_seq', 1, true);
SELECT pg_catalog.setval('public.canchas_id_seq', 8, true);
SELECT pg_catalog.setval('public.clientes_id_seq', 5, true);
SELECT pg_catalog.setval('public.pagos_id_seq', 3, true);
SELECT pg_catalog.setval('public.reservas_id_seq', 9, true);
SELECT pg_catalog.setval('public.tipos_cancha_id_seq', 31, true);
SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);

-- =====================================================
-- INSERTS DE DATOS
-- =====================================================

-- =====================================================
-- TABLA: usuarios
-- =====================================================

INSERT INTO public.usuarios (id, username, email, password, nombre, apellido, rol, estado, telefono, fecha_creacion, fecha_actualizacion) VALUES
(1, 'admin', 'admin@sportcourt.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrador', 'Sistema', 'admin_reservas', 'Activo', NULL, '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297');

-- =====================================================
-- TABLA: tipos_cancha
-- =====================================================

INSERT INTO public.tipos_cancha (id, nombre, descripcion, precio_por_hora, estado, fecha_creacion, fecha_actualizacion) VALUES
(1, 'Fútbol 11', 'Cancha de fútbol para 11 jugadores', 50.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(2, 'Fútbol 7', 'Cancha de fútbol para 7 jugadores', 40.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(3, 'Basketball', 'Cancha de baloncesto', 35.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(4, 'Tennis', 'Cancha de tenis', 45.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(5, 'Voleibol', 'Cancha de voleibol', 30.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(6, 'Fútbol 5', 'Cancha de fútbol para 5 jugadores', 35.00, 'Activo', '2025-07-31 11:38:53.28448', '2025-07-31 11:38:53.28448'),
(13, 'Tenis', 'Cancha de tenis', 80.00, 'Activo', '2025-07-31 12:45:50.268719', '2025-07-31 12:45:50.268719'),
(14, 'prueba', 'prueba', 50.00, 'Activo', '2025-08-01 16:50:39.002218', '2025-08-01 16:50:39.002218'),
(15, 'prueba 2', 'prueba 2', 50.00, 'Activo', '2025-08-01 16:56:27.150779', '2025-08-01 16:56:27.150779'),
(26, 'Padel', 'cancha de padel', 100.00, 'Activo', '2025-08-02 19:22:47.697449', '2025-08-02 19:22:47.697449');

-- =====================================================
-- TABLA: clientes
-- =====================================================

INSERT INTO public.clientes (id, nombre, apellido, email, telefono, direccion, fecha_nacimiento, estado, fecha_registro, fecha_actualizacion) VALUES
(1, 'Juan', 'Pérez', 'juan.perez@email.com', '3001234567', 'Calle 123 #45-67', '1990-05-15', 'Activo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(2, 'María', 'González', 'maria.gonzalez@email.com', '3002345678', 'Carrera 78 #90-12', '1985-08-22', 'Activo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(3, 'Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '3003456789', 'Avenida 5 #23-45', '1992-12-10', 'Activo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(4, 'Ana', 'López', 'ana.lopez@email.com', '3004567890', 'Calle 90 #12-34', '1988-03-28', 'Activo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(5, 'Luis', 'Martínez', 'luis.martinez@email.com', '3005678901', 'Carrera 45 #67-89', '1995-07-14', 'Activo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297');

-- =====================================================
-- TABLA: canchas
-- =====================================================

INSERT INTO public.canchas (id, nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion, fecha_creacion, fecha_actualizacion, tipo_cancha_id) VALUES
(1, 'Cancha Elefante', 'Fútbol', 100, 50.00, 'Activa', '06:00:00', '22:00:00', 'Cancha de fútbol 11 con césped sintético', '2025-07-31 11:20:41.988297', '2025-08-01 17:07:43.665966', 1),
(2, 'Cancha 2 - Fútbol', 'Fútbol', 100, 50.00, 'Activa', '06:00:00', '22:00:00', 'Cancha de fútbol 11 con césped sintético', '2025-07-31 11:20:41.988297', '2025-07-31 11:38:53.28448', 1),
(3, 'Cancha 3 - Basketball', 'Basketball', 50, 40.00, 'Activa', '06:00:00', '22:00:00', 'Cancha de basketball con piso de madera', '2025-07-31 11:20:41.988297', '2025-07-31 11:38:53.28448', 1),
(4, 'Cancha 4 - Tennis', 'Tennis', 30, 60.00, 'Activa', '06:00:00', '22:00:00', 'Cancha de tennis con superficie de arcilla', '2025-07-31 11:20:41.988297', '2025-07-31 11:38:53.28448', 1),
(5, 'Cancha 5 - Voleibol', 'Voleibol', 40, 35.00, 'Activa', '06:00:00', '22:00:00', 'Cancha de voleibol de arena', '2025-07-31 11:20:41.988297', '2025-07-31 11:38:53.28448', 1),
(7, 'prueba 2', 'Fútbol', 50, 50.00, 'Activa', '06:00:00', '22:00:00', 'prueba operador', '2025-08-01 16:56:27.162001', '2025-08-01 16:56:27.162001', 15);

-- =====================================================
-- TABLA: reservas
-- =====================================================

INSERT INTO public.reservas (id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, duracion, estado, observaciones, fecha_creacion, fecha_actualizacion) VALUES
(1, 1, 1, '2025-08-01', '14:00:00', '16:00:00', 2.00, 'Confirmada', 'Partido de fútbol', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(2, 2, 3, '2025-08-02', '16:00:00', '18:00:00', 2.00, 'Pendiente', 'Entrenamiento de basketball', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(3, 3, 4, '2025-08-03', '10:00:00', '11:00:00', 1.00, 'Confirmada', 'Clase de tennis', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(4, 4, 5, '2025-08-01', '18:00:00', '20:00:00', 2.00, 'Pendiente', 'Torneo de voleibol', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(5, 5, 2, '2025-08-04', '20:00:00', '22:00:00', 2.00, 'Confirmada', 'Partido nocturno', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(8, 4, 2, '2025-08-02', '14:00:00', '16:00:00', 2.00, 'pendiente', NULL, '2025-08-02 19:07:35.906714', '2025-08-02 19:07:35.906714'),
(9, 2, 7, '2025-08-02', '14:00:00', '18:00:00', 4.00, 'pendiente', NULL, '2025-08-02 19:07:52.007044', '2025-08-02 19:07:52.007044');

-- =====================================================
-- TABLA: pagos
-- =====================================================

INSERT INTO public.pagos (id, reserva_id, cliente_id, monto, metodo_pago, estado, fecha_pago, observaciones, fecha_creacion, fecha_actualizacion) VALUES
(1, 1, 1, 100.00, 'Efectivo', 'Completado', '2025-07-31', 'Pago en efectivo', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(2, 3, 3, 60.00, 'Tarjeta de Crédito', 'Completado', '2025-07-31', 'Pago con tarjeta', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297'),
(3, 5, 5, 100.00, 'Transferencia', 'Completado', '2025-07-31', 'Transferencia bancaria', '2025-07-31 11:20:41.988297', '2025-07-31 11:20:41.988297');

-- =====================================================
-- TABLA: auditoria
-- =====================================================

INSERT INTO public.auditoria (id, usuario_id, tipo_accion, tabla, registro_id, detalles, resultado, ip_address, fecha_hora) VALUES
(1, NULL, 'DELETE', 'canchas', 6, 'Registro eliminado', 'SUCCESS', '127.0.0.1', '2025-08-02 19:27:57.898328');

-- =====================================================
-- RESUMEN DE DATOS INSERTADOS
-- =====================================================

/*
RESUMEN DE INSERTS REALIZADOS:

1. USUARIOS: 1 registro
   - Administrador del sistema

2. TIPOS_CANCHA: 10 registros
   - Fútbol 11, Fútbol 7, Basketball, Tennis, Voleibol, Fútbol 5, Tenis, prueba, prueba 2, Padel

3. CLIENTES: 5 registros
   - Juan Pérez, María González, Carlos Rodríguez, Ana López, Luis Martínez

4. CANCHAS: 6 registros
   - Cancha Elefante, Cancha 2 - Fútbol, Cancha 3 - Basketball, Cancha 4 - Tennis, Cancha 5 - Voleibol, prueba 2

5. RESERVAS: 7 registros
   - Reservas para diferentes canchas con estados Confirmada y Pendiente

6. PAGOS: 3 registros
   - Pagos completados para reservas confirmadas

7. AUDITORIA: 1 registro
   - Registro de eliminación de cancha

TOTAL: 33 registros insertados
*/

-- =====================================================
-- VERIFICACIÓN DE DATOS
-- =====================================================

-- Verificar que los datos se insertaron correctamente
SELECT 'USUARIOS' as tabla, COUNT(*) as total FROM usuarios
UNION ALL
SELECT 'TIPOS_CANCHA', COUNT(*) FROM tipos_cancha
UNION ALL
SELECT 'CLIENTES', COUNT(*) FROM clientes
UNION ALL
SELECT 'CANCHAS', COUNT(*) FROM canchas
UNION ALL
SELECT 'RESERVAS', COUNT(*) FROM reservas
UNION ALL
SELECT 'PAGOS', COUNT(*) FROM pagos
UNION ALL
SELECT 'AUDITORIA', COUNT(*) FROM auditoria
ORDER BY tabla;

-- =====================================================
-- DATOS INSERTADOS COMPLETADOS
-- ===================================================== 