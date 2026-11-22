-- Migración a la entrega final. Ejecutar UNA vez si ya tenías la base importada.
-- (Si importas mascotas_rest_db.sql desde cero NO hace falta: ya incluye todo.)
USE mascotas_rest_db;

ALTER TABLE mascotas ADD COLUMN foto_url VARCHAR(255) NULL AFTER descripcion;

CREATE TABLE IF NOT EXISTS `notificaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` enum('nuevo_reporte','avistamiento','encontrada','reclamo') NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `reporte_id` int DEFAULT NULL,
  `mascota_id` int DEFAULT NULL,
  `usuario_id` int NOT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `lecturas_notificaciones` (
  `usuario_id` int NOT NULL,
  `ultima_id` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `lecturas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `planes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `publico` varchar(120) NOT NULL,
  `precio_mes` int NOT NULL DEFAULT 0,
  `precio_anio` int NOT NULL DEFAULT 0,
  `destacado` tinyint NOT NULL DEFAULT 0,
  `caracteristicas` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `suscripciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `plan_id` int NOT NULL,
  `periodo` enum('mensual','anual') NOT NULL,
  `organizacion` varchar(120) DEFAULT NULL,
  `estado` enum('activa','cancelada') NOT NULL DEFAULT 'activa',
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `vence_en` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `plan_id` (`plan_id`),
  CONSTRAINT `suscripciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `suscripciones_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `planes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT IGNORE INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (1,'comunidad','Comunidad','Para cualquier persona que quiera ayudar',0,0,0,'["Ver todas las mascotas perdidas y encontradas", "Buscar con filtros por ciudad, raza, color y especie", "Reportar hasta 3 mascotas activas", "Notificaciones de la comunidad"]');
INSERT IGNORE INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (2,'hogar','Hogar','Para familias con mascotas',9900,99000,0,'["Todo lo del plan Comunidad", "Reportes ilimitados", "Alertas prioritarias cuando alguien ve a tu mascota", "Cartel descargable para compartir en redes", "Soporte por correo"]');
INSERT IGNORE INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (3,'fundacion','Fundación','Para fundaciones, refugios y rescatistas',39900,399000,1,'["Todo lo del plan Hogar", "Perfil de la organización con logo", "Hasta 100 reportes activos a la vez", "Reporte mensual de mascotas reunidas", "Insignia de fundación verificada", "Soporte prioritario por WhatsApp"]');
INSERT IGNORE INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (4,'institucional','Institucional','Para veterinarias, alcaldías y universidades',119900,1199000,0,'["Todo lo del plan Fundación", "Reportes ilimitados y varias sedes", "Varios usuarios administradores", "Estadísticas por ciudad y por especie", "Acompañamiento para campañas de adopción"]');

-- Los datos de ejemplo extra (más mascotas y reportes) vienen en mascotas_rest_db.sql.
