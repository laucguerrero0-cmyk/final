-- Migración: contacto (teléfono), historial de novedades y avisos dirigidos.
--
-- NO ES OBLIGATORIO ejecutarla: los servicios de Render hacen estos mismos cambios solos al arrancar
-- (ver backend/common/migraciones.py). Úsala solo si prefieres aplicarlos tú a mano en TiDB.
--
-- Solo AGREGA columnas y una tabla; no borra ni modifica ningún dato existente.
-- Si una columna ya existe, esa línea dará "Duplicate column name": es normal, sigue con la siguiente.
USE mascotas_rest_db;

ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20) NULL AFTER correo;

ALTER TABLE notificaciones ADD COLUMN destinatario_id INT NULL;

CREATE TABLE IF NOT EXISTS `novedades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reporte_id` int NOT NULL,
  `mascota_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `tipo` enum('avistamiento','hallazgo','reclamo','resuelto') NOT NULL,
  `estado` enum('abierta','confirmada','descartada') NOT NULL DEFAULT 'abierta',
  `lugar` varchar(120) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `condicion` varchar(60) DEFAULT NULL,
  `hace_minutos` int DEFAULT NULL,
  `compartir_contacto` tinyint NOT NULL DEFAULT 0,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_novedades_reporte` (`reporte_id`),
  KEY `idx_novedades_mascota` (`mascota_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
