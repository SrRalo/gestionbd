# LISTADO COMPLETO DE FUNCIONES, VISTAS, TRIGGERS Y PROCEDIMIENTOS ALMACENADOS

## Resumen Ejecutivo

Este documento contiene el listado completo de todos los elementos de base de datos utilizados en el proyecto **SportCourt Reservations - Sistema de Gestión de Reservas**.

### Estadísticas Generales:
- **Funciones Almacenadas:** 23 funciones
- **Procedimientos Almacenados:** 5 procedimientos
- **Vistas Definidas:** 4 vistas
- **Vistas Referenciadas pero No Definidas:** 3 vistas
- **Triggers:** 12 triggers

**Total: 47 elementos de base de datos identificados**

---

## FUNCIONES ALMACENADAS (PL/pgSQL)

### Funciones de Auditoría

#### 1. `actualizar_fecha_tipos_cancha()`
- **Descripción:** Función trigger para actualizar fecha de tipos de cancha
- **Definida en:** `backup.txt` (línea 333)
- **Archivo que la usa:** Trigger `trigger_actualizar_fecha_tipos_cancha`
- **Tipo:** Trigger Function

#### 2. `update_updated_at_column()`
- **Descripción:** Función trigger para actualizar columnas updated_at
- **Definida en:** `backup.txt` (línea 344)
- **Archivo que la usa:** Múltiples triggers de actualización
- **Tipo:** Trigger Function

#### 3. `registrar_auditoria_automatica()`
- **Descripción:** Función trigger para auditoría automática
- **Definida en:** `backup.txt` (línea 355)
- **Archivo que la usa:** Triggers de auditoría en todas las tablas
- **Tipo:** Trigger Function

### Funciones de Canchas

#### 4. `verificar_disponibilidad_cancha(p_cancha_id, p_fecha, p_hora_inicio, p_hora_fin)`
- **Descripción:** Verifica disponibilidad de cancha
- **Parámetros:** 
  - `p_cancha_id` (integer): ID de la cancha
  - `p_fecha` (date): Fecha de la reserva
  - `p_hora_inicio` (time): Hora de inicio
  - `p_hora_fin` (time): Hora de fin
- **Retorna:** boolean
- **Usada en:** `capa_datos/reservas_data.py` (línea 362)
- **Archivo que la usa:** `verificar_disponibilidad_db()`

#### 5. `obtener_canchas()`
- **Descripción:** Obtiene todas las canchas
- **Retorna:** TABLE con información de canchas
- **Definida en:** `backup.txt` (línea 475)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 6. `obtener_tipos_cancha()`
- **Descripción:** Obtiene todos los tipos de cancha
- **Retorna:** TABLE con información de tipos de cancha
- **Definida en:** `backup.txt` (línea 490)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 7. `crear_tipo_cancha(p_nombre, p_descripcion, p_precio_por_hora)`
- **Descripción:** Crea tipo de cancha
- **Parámetros:**
  - `p_nombre` (varchar): Nombre del tipo
  - `p_descripcion` (text): Descripción
  - `p_precio_por_hora` (numeric): Precio por hora
- **Retorna:** integer (ID del tipo creado)
- **Usada en:** `capa_datos/canchas_data.py` (línea 543)
- **Archivo que la usa:** `crear_tipo_cancha_db()`

#### 8. `eliminar_tipo_cancha(p_id)`
- **Descripción:** Elimina tipo de cancha
- **Parámetros:** `p_id` (integer): ID del tipo a eliminar
- **Retorna:** boolean
- **Usada en:** `capa_datos/canchas_data.py` (línea 639)
- **Archivo que la usa:** `eliminar_tipo_cancha_db()`

#### 9. `actualizar_tipo_cancha(p_id, p_nombre, p_descripcion, p_precio_por_hora, p_activo)`
- **Descripción:** Actualiza tipo de cancha
- **Parámetros:**
  - `p_id` (integer): ID del tipo
  - `p_nombre` (varchar): Nuevo nombre
  - `p_descripcion` (text): Nueva descripción
  - `p_precio_por_hora` (numeric): Nuevo precio
  - `p_activo` (boolean): Estado activo/inactivo
- **Retorna:** boolean
- **Usada en:** `capa_datos/canchas_data.py` (línea 578)
- **Archivo que la usa:** `actualizar_tipo_cancha_db()`

#### 10. `obtener_cancha_por_id(p_id)`
- **Descripción:** Obtiene cancha por ID
- **Parámetros:** `p_id` (integer): ID de la cancha
- **Retorna:** TABLE con información de la cancha
- **Definida en:** `backup.txt` (línea 633)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 11. `obtener_canchas_con_tipos()`
- **Descripción:** Obtiene canchas con información de tipos
- **Retorna:** TABLE con canchas y sus tipos
- **Definida en:** `backup.txt` (línea 675)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 12. `buscar_canchas_por_deporte(p_tipo_deporte)`
- **Descripción:** Busca canchas por deporte
- **Parámetros:** `p_tipo_deporte` (varchar): Tipo de deporte
- **Retorna:** TABLE con canchas del deporte especificado
- **Definida en:** `backup.txt` (línea 928)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 13. `crear_cancha(p_nombre, p_tipo_deporte, p_capacidad, p_precio_hora, p_estado, p_horario_apertura, p_horario_cierre, p_descripcion, p_tipo_cancha_id)`
- **Descripción:** Crea cancha
- **Parámetros:** Múltiples parámetros para crear una cancha
- **Retorna:** integer (ID de la cancha creada)
- **Usada en:** `capa_datos/canchas_data.py` (línea 508)
- **Archivo que la usa:** `crear_cancha_db()`

#### 14. `actualizar_cancha(p_id, p_nombre, p_tipo_deporte, p_capacidad, p_precio_hora, p_estado, p_horario_apertura, p_horario_cierre, p_descripcion, p_tipo_cancha_id)`
- **Descripción:** Actualiza cancha
- **Parámetros:** Múltiples parámetros para actualizar una cancha
- **Retorna:** boolean
- **Usada en:** `capa_datos/canchas_data.py` (línea 613)
- **Archivo que la usa:** `actualizar_cancha_db()`

#### 15. `eliminar_cancha(p_id)`
- **Descripción:** Elimina cancha
- **Parámetros:** `p_id` (integer): ID de la cancha a eliminar
- **Retorna:** boolean
- **Usada en:** `capa_datos/canchas_data.py` (línea 663)
- **Archivo que la usa:** `eliminar_cancha_db()`

### Funciones de Clientes

#### 16. `crear_cliente(p_nombre, p_apellido, p_telefono, p_email, p_fecha_nacimiento)`
- **Descripción:** Crea cliente
- **Parámetros:** Datos del cliente
- **Retorna:** integer (ID del cliente creado)
- **Definida en:** `backup.txt` (línea 721)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 17. `actualizar_cliente(p_id, p_nombre, p_apellido, p_telefono, p_email, p_fecha_nacimiento, p_estado)`
- **Descripción:** Actualiza cliente
- **Parámetros:** Datos actualizados del cliente
- **Retorna:** boolean
- **Definida en:** `backup.txt` (línea 769)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 18. `eliminar_cliente(p_id)`
- **Descripción:** Elimina cliente
- **Parámetros:** `p_id` (integer): ID del cliente a eliminar
- **Retorna:** boolean
- **Definida en:** `backup.txt` (línea 830)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 19. `obtener_cliente_por_id(p_id)`
- **Descripción:** Obtiene cliente por ID
- **Parámetros:** `p_id` (integer): ID del cliente
- **Retorna:** TABLE con información del cliente
- **Definida en:** `backup.txt` (línea 866)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 20. `obtener_clientes()`
- **Descripción:** Obtiene todos los clientes
- **Retorna:** TABLE con todos los clientes
- **Definida en:** `backup.txt` (línea 897)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 21. `obtener_estadisticas_cliente(p_cliente_id)`
- **Descripción:** Obtiene estadísticas de cliente
- **Parámetros:** `p_cliente_id` (integer): ID del cliente
- **Retorna:** TABLE con estadísticas del cliente
- **Definida en:** `backup.txt` (línea 968)
- **Archivo que la usa:** No se usa directamente en el código Python

### Funciones de Reservas

#### 22. `crear_reserva(p_cliente_id, p_cancha_id, p_fecha_reserva, p_hora_inicio, p_hora_fin, p_observaciones)`
- **Descripción:** Crea reserva
- **Parámetros:** Datos de la reserva
- **Retorna:** integer (ID de la reserva creada)
- **Definida en:** `backup.txt` (línea 438)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 23. `verificar_disponibilidad_rango(p_cancha_id, p_fecha_inicio, p_fecha_fin, p_hora_inicio, p_hora_fin)`
- **Descripción:** Verifica disponibilidad en rango
- **Parámetros:** Rango de fechas y horas
- **Retorna:** boolean
- **Definida en:** `backup.txt` (línea 1005)
- **Archivo que la usa:** No se usa directamente en el código Python

---

## PROCEDIMIENTOS ALMACENADOS

### Procedimientos de Pagos

#### 24. `proc_registrar_pago(p_reserva_id, p_monto, p_metodo_pago, p_observaciones)`
- **Descripción:** Registra pago
- **Parámetros:**
  - `p_reserva_id` (integer): ID de la reserva
  - `p_monto` (numeric): Monto del pago
  - `p_metodo_pago` (varchar): Método de pago
  - `p_observaciones` (text): Observaciones
- **Usado en:** `capa_datos/pagos_data.py` (línea 19)
- **Archivo que lo usa:** `registrar_pago_db()`

### Procedimientos de Reservas

#### 25. `proc_gestionar_reserva(p_accion, p_reserva_id, p_cliente_id, p_cancha_id, p_fecha_reserva, p_hora_inicio, p_hora_fin, p_observaciones, p_estado)`
- **Descripción:** Gestiona reservas (CREATE/UPDATE/CANCEL)
- **Parámetros:** Múltiples parámetros para gestionar reservas
- **Usado en:** `capa_datos/reservas_data.py` (líneas 28, 144, 188)
- **Archivo que lo usa:** `crear_reserva_db()`, `actualizar_reserva_db()`, `cancelar_reserva_db()`

### Procedimientos de Auditoría

#### 26. `proc_registrar_auditoria_manual(p_tipo_accion, p_usuario_id, p_tabla, p_registro_id, p_detalles, p_ip_address)`
- **Descripción:** Registra auditoría manual
- **Parámetros:**
  - `p_tipo_accion` (varchar): Tipo de acción
  - `p_usuario_id` (integer): ID del usuario
  - `p_tabla` (varchar): Tabla afectada
  - `p_registro_id` (integer): ID del registro
  - `p_detalles` (text): Detalles de la acción
  - `p_ip_address` (varchar): Dirección IP
- **Usado en:** `capa_datos/auditoria_data.py` (línea 34)
- **Archivo que lo usa:** `registrar_accion_auditoria()`

### Procedimientos de Validación

#### 27. `proc_validar_y_limpiar_datos(p_tabla, p_accion)`
- **Descripción:** Valida y limpia datos
- **Parámetros:**
  - `p_tabla` (varchar): Nombre de la tabla
  - `p_accion` (varchar): Acción a realizar (VALIDATE/CLEAN/BACKUP)
- **Usado en:** `capa_datos/validacion_data.py` (líneas 17, 43, 69)
- **Archivo que lo usa:** `validar_datos_db()`, `limpiar_datos_db()`, `crear_backup_db()`

### Procedimientos de Reportes

#### 28. `proc_generar_estadisticas(p_fecha_inicio, p_fecha_fin, p_tipo_reporte)`
- **Descripción:** Genera estadísticas
- **Parámetros:**
  - `p_fecha_inicio` (date): Fecha de inicio
  - `p_fecha_fin` (date): Fecha de fin
  - `p_tipo_reporte` (varchar): Tipo de reporte
- **Usado en:** `capa_datos/reports_data.py` (línea 20)
- **Archivo que lo usa:** `generar_estadisticas_procedimiento_db()`

---

## VISTAS

### Vistas Definidas

#### 29. `vista_reservas_completa`
- **Descripción:** Vista completa de reservas con información de clientes y canchas
- **Definida en:** `backup.txt` (línea 1463)
- **Archivo que la usa:** No se usa directamente en el código Python

#### 30. `vista_reservas_pendientes_pago`
- **Descripción:** Vista de reservas pendientes de pago
- **Definida en:** `backup.txt` (línea 1487)
- **Archivo que la usa:** `vistas/pagos_view.py` (línea 327)

#### 31. `vista_historial_pagos`
- **Descripción:** Vista de historial de pagos
- **Definida en:** `backup.txt` (línea 1528)
- **Archivo que la usa:** `vistas/pagos_view.py` (línea 386)

#### 32. `vista_canchas_disponibles`
- **Descripción:** Vista de canchas disponibles con estadísticas
- **Definida en:** `backup.txt` (línea 1562)
- **Archivo que la usa:** No se usa directamente en el código Python

### Vistas Referenciadas pero No Definidas

#### 33. `vista_reporte_reservas`
- **Descripción:** Vista de reporte de reservas (referenciada pero no definida)
- **Referenciada en:** `capa_datos/reports_data.py` (línea 48)
- **Archivo que la usa:** `get_vista_reservas_completas_db()`
- **Estado:** ❌ **FALTANTE** - Necesita ser definida

#### 34. `vista_canchas_mas_usadas`
- **Descripción:** Vista de canchas más usadas (referenciada pero no definida)
- **Referenciada en:** `capa_datos/reports_data.py` (línea 83)
- **Archivo que la usa:** `get_vista_estadisticas_canchas_db()`
- **Estado:** ❌ **FALTANTE** - Necesita ser definida

#### 35. `vista_resumen_pagos_periodo`
- **Descripción:** Vista de resumen de pagos por período (referenciada pero no definida)
- **Referenciada en:** `vistas/pagos_view.py` (línea 408)
- **Archivo que la usa:** `vistas/pagos_view.py`
- **Estado:** ❌ **FALTANTE** - Necesita ser definida

---

## TRIGGERS

### Triggers de Auditoría

#### 36. `trigger_auditoria_canchas`
- **Descripción:** Trigger para auditoría automática en tabla canchas
- **Definido en:** `backup.txt` (línea 1387)
- **Función asociada:** `registrar_auditoria_automatica()`
- **Tabla:** canchas

#### 37. `trigger_auditoria_clientes`
- **Descripción:** Trigger para auditoría automática en tabla clientes
- **Definido en:** `backup.txt` (línea 1394)
- **Función asociada:** `registrar_auditoria_automatica()`
- **Tabla:** clientes

#### 38. `trigger_auditoria_reservas`
- **Descripción:** Trigger para auditoría automática en tabla reservas
- **Definido en:** `backup.txt` (línea 1401)
- **Función asociada:** `registrar_auditoria_automatica()`
- **Tabla:** reservas

#### 39. `trigger_auditoria_tipos_cancha`
- **Descripción:** Trigger para auditoría automática en tabla tipos_cancha
- **Definido en:** `backup.txt` (línea 1408)
- **Función asociada:** `registrar_auditoria_automatica()`
- **Tabla:** tipos_cancha

#### 40. `trigger_auditoria_usuarios`
- **Descripción:** Trigger para auditoría automática en tabla usuarios
- **Definido en:** `backup.txt` (línea 1415)
- **Función asociada:** `registrar_auditoria_automatica()`
- **Tabla:** usuarios

### Triggers de Actualización de Fechas

#### 41. `trigger_actualizar_fecha_tipos_cancha`
- **Descripción:** Trigger para actualizar fecha en tipos_cancha
- **Definido en:** `backup.txt` (línea 1380)
- **Función asociada:** `actualizar_fecha_tipos_cancha()`
- **Tabla:** tipos_cancha

#### 42. `update_canchas_updated_at`
- **Descripción:** Trigger para actualizar updated_at en canchas
- **Definido en:** `backup.txt` (línea 1422)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** canchas

#### 43. `update_clientes_updated_at`
- **Descripción:** Trigger para actualizar updated_at en clientes
- **Definido en:** `backup.txt` (línea 1428)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** clientes

#### 44. `update_pagos_updated_at`
- **Descripción:** Trigger para actualizar updated_at en pagos
- **Definido en:** `backup.txt` (línea 1434)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** pagos

#### 45. `update_reservas_updated_at`
- **Descripción:** Trigger para actualizar updated_at en reservas
- **Definido en:** `backup.txt` (línea 1440)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** reservas

#### 46. `update_tipos_cancha_updated_at`
- **Descripción:** Trigger para actualizar updated_at en tipos_cancha
- **Definido en:** `backup.txt` (línea 1446)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** tipos_cancha

#### 47. `update_usuarios_updated_at`
- **Descripción:** Trigger para actualizar updated_at en usuarios
- **Definido en:** `backup.txt` (línea 1452)
- **Función asociada:** `update_updated_at_column()`
- **Tabla:** usuarios

---

## NOTAS IMPORTANTES

### ⚠️ Elementos Faltantes
Las siguientes vistas están referenciadas en el código pero **NO están definidas** en el `backup.txt`:

1. `vista_reporte_reservas` - Referenciada en `capa_datos/reports_data.py`
2. `vista_canchas_mas_usadas` - Referenciada en `capa_datos/reports_data.py`
3. `vista_resumen_pagos_periodo` - Referenciada en `vistas/pagos_view.py`

### 📊 Funciones No Utilizadas
Muchas funciones SQL están definidas en el `backup.txt` pero no se usan directamente en el código Python, posiblemente porque se implementaron operaciones directas con SQL.

### 🔄 Triggers Automáticos
Los triggers de auditoría y actualización de fechas funcionan automáticamente sin necesidad de llamadas explícitas desde el código Python.

### ⭐ Procedimientos Principales
Los procedimientos más importantes son:
- `proc_gestionar_reserva` - Gestión de reservas
- `proc_registrar_auditoria_manual` - Auditoría manual
- `proc_validar_y_limpiar_datos` - Validación y limpieza de datos

Estos son utilizados activamente por la aplicación.

---

## ARCHIVOS PRINCIPALES DEL PROYECTO

### Capa de Datos (`capa_datos/`)
- `reservas_data.py` - Funciones de reservas
- `canchas_data.py` - Funciones de canchas
- `clientes_data.py` - Funciones de clientes
- `pagos_data.py` - Funciones de pagos
- `auditoria_data.py` - Funciones de auditoría
- `validacion_data.py` - Funciones de validación
- `reports_data.py` - Funciones de reportes
- `usuarios_data.py` - Funciones de usuarios

### Lógica de Negocio (`logica_negocio/`)
- `reservas_logic.py` - Lógica de reservas
- `canchas_logic.py` - Lógica de canchas
- `clientes_logic.py` - Lógica de clientes
- `pagos_logic.py` - Lógica de pagos
- `auditoria_logic.py` - Lógica de auditoría
- `validacion_logic.py` - Lógica de validación
- `reports_logic.py` - Lógica de reportes

### Vistas (`vistas/`)
- `reservas_view.py` - Interfaz de reservas
- `canchas_view.py` - Interfaz de canchas
- `clientes_view.py` - Interfaz de clientes
- `pagos_view.py` - Interfaz de pagos
- `auditoria_view.py` - Interfaz de auditoría
- `validacion_view.py` - Interfaz de validación
- `reports_view.py` - Interfaz de reportes

---

*Documento generado automáticamente - Fecha: 2025-01-27*
*Proyecto: SportCourt Reservations - Sistema de Gestión de Reservas* 