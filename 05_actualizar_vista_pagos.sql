-- =====================================================
-- ACTUALIZACIÓN DE VISTA PARA RESERVAS PENDIENTES DE PAGO
-- =====================================================

-- Eliminar la vista existente si existe
DROP VIEW IF EXISTS public.vista_reservas_pendientes_pago;

-- Crear la vista actualizada que reconoce estados en minúsculas y mayúsculas
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
WHERE r.estado IN ('confirmada', 'pendiente', 'Confirmada', 'Pendiente')
GROUP BY r.id, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion, r.estado, r.observaciones,
         c.id, c.nombre, c.apellido, c.email, c.telefono,
         ca.id, ca.nombre, ca.tipo_deporte, ca.precio_hora, r.fecha_creacion, r.fecha_actualizacion
HAVING COALESCE(SUM(p.monto), 0) < (r.duracion * ca.precio_hora)
ORDER BY r.fecha_reserva DESC, r.hora_inicio;

-- Otorgar permisos a la vista
GRANT ALL ON TABLE public.vista_reservas_pendientes_pago TO admin_reservas;
GRANT SELECT ON TABLE public.vista_reservas_pendientes_pago TO operador_reservas;
GRANT SELECT ON TABLE public.vista_reservas_pendientes_pago TO consultor_reservas;

-- Verificar que la vista funciona correctamente
-- Comentario: Puedes ejecutar esta consulta para verificar que las reservas aparecen
-- SELECT * FROM vista_reservas_pendientes_pago LIMIT 5;