SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol` enum('admin','usuario') NOT NULL DEFAULT 'usuario',
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `usuarios` (`id`, `nombre`, `usuario`, `correo`, `password_hash`, `rol`, `creado_en`) VALUES (1, 'Administrador del sistema', 'admin', 'admin@mascotas.com', 'pbkdf2:sha256:1000000$NhnwOzsbnK5vbybU$a9f0f8245bfa6646da6c7936d0ed738810c848ae4cdac2a25cea65d302e5ca18', 'admin', '2026-10-13 21:39:59');
INSERT INTO `usuarios` (`id`, `nombre`, `usuario`, `correo`, `password_hash`, `rol`, `creado_en`) VALUES (2, 'Laura Catalina Guerrero Paz', 'laura', 'laura@mascotas.com', 'pbkdf2:sha256:1000000$JAFC8T8OqdMNTnbB$c7885813cf788d4a746d6e2550e111d64d9f26959f48f969333b2c5c314f0bb5', 'usuario', '2026-10-13 21:39:59');
INSERT INTO `usuarios` (`id`, `nombre`, `usuario`, `correo`, `password_hash`, `rol`, `creado_en`) VALUES (3, 'Juan David Barrera Torres', 'juan', 'juan@mascotas.com', 'pbkdf2:sha256:1000000$gfxvzCw5DBn5r0SR$b4626574ac2ca9a2a8dde3fb9073b76fc2eabe8dd02fd7d6332213a46e2d3f14', 'usuario', '2026-10-13 21:39:59');


DROP TABLE IF EXISTS `mascotas`;
CREATE TABLE `mascotas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `especie` varchar(40) NOT NULL,
  `raza` varchar(60) DEFAULT NULL,
  `color` varchar(40) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `foto_url` varchar(255) DEFAULT NULL,
  `usuario_id` int NOT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `mascotas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (1,'Luna','Perro','Labrador','Negro','Collar rojo, muy cariñosa',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (2,'Max','Perro','Pastor','Blanco','Tiene una mancha café en la oreja',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (3,'Miel','Gato','Criollo','Naranja','Ojos verdes, tamaño mediano',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (4,'Rocky','Perro','Criollo','Café','Cicatriz en la pata trasera',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (5,'Nieve','Gato','Angora','Blanco','Pelo largo, collar azul',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (6,'Toby','Perro','Golden Retriever','Dorado','Responde al nombre, muy juguetón',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (7,'Canela','Perro','Beagle','Café','Muy sociable, collar verde',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (8,'Pelusa','Gato','Persa','Gris','Ojos azules, pelo largo y suave',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (9,'Bruno','Perro','Bulldog','Blanco','Mancha negra alrededor del ojo',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (10,'Simba','Gato','Criollo','Naranja','Pelaje rayado, cola larga',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (11,'Coco','Perro','Poodle','Blanco','Sin collar, muy dócil',3,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (12,'Sin nombre','Gato','Criollo','Gris','Joven, con un pequeño corte en la oreja',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (13,'Kira','Perro','Husky','Gris','Un ojo azul y otro café',2,'2026-11-01 09:00:00');
INSERT INTO `mascotas` (`id`,`nombre`,`especie`,`raza`,`color`,`descripcion`,`usuario_id`,`creado_en`) VALUES (14,'Mora','Gato','Criollo','Negro','Ojos amarillos, muy asustadiza',3,'2026-11-01 09:00:00');


DROP TABLE IF EXISTS `reportes`;
CREATE TABLE `reportes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mascota_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `tipo` enum('perdida','encontrada') NOT NULL,
  `lugar` varchar(120) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `estado` enum('abierto','resuelto') NOT NULL DEFAULT 'abierto',
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `mascota_id` (`mascota_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `reportes_ibfk_1` FOREIGN KEY (`mascota_id`) REFERENCES `mascotas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reportes_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (1,1,2,'perdida','Popayán - Parque Caldas','Se perdió cerca al parque en la tarde','resuelto','2026-11-02 16:00:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (2,2,3,'perdida','Popayán - Barrio Bolívar','Salió por la puerta del jardín','abierto','2026-11-12 18:30:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (3,3,2,'encontrada','Popayán - El Empedrado','Encontrada sin collar','abierto','2026-11-14 10:15:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (4,4,3,'perdida','Cali - Barrio San Fernando','Se escapó durante un paseo','abierto','2026-11-10 07:45:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (5,5,2,'encontrada','Popayán - Parque Caldas','Muy asustada, está en una veterinaria','abierto','2026-11-15 12:00:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (6,6,3,'perdida','Popayán - Campus Unicomfacauca','Visto por última vez en la portería','abierto','2026-11-16 08:20:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (7,7,2,'perdida','Bogotá - Chapinero','Se soltó de la correa en el parque','abierto','2026-11-13 17:10:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (8,8,3,'perdida','Medellín - El Poblado','Salió por la ventana del segundo piso','abierto','2026-11-15 21:00:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (9,9,2,'perdida','Cali - Granada','Se perdió después de un paseo nocturno','abierto','2026-11-11 20:40:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (10,10,3,'perdida','Popayán - Barrio Modelo','No volvió a casa desde el lunes','abierto','2026-11-16 19:05:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (11,11,3,'encontrada','Popayán - Parque Caldas','Anda sola cerca de la fuente, está bien cuidada','abierto','2026-11-16 15:30:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (12,12,2,'encontrada','Bogotá - Usaquén','Fue entregada a su familia','resuelto','2026-11-09 11:00:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (13,13,2,'perdida','Medellín - Laureles','Se escapó al abrir el portón','abierto','2026-11-17 07:30:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (14,14,3,'perdida','Popayán - Centro','Se asustó con la pólvora y salió corriendo','abierto','2026-11-09 22:10:00');
INSERT INTO `reportes` (`id`,`mascota_id`,`usuario_id`,`tipo`,`lugar`,`descripcion`,`estado`,`fecha`) VALUES (15,1,3,'encontrada','Popayán - Parque Caldas','La encontró una vecina y la devolvió','resuelto','2026-11-03 09:30:00');


DROP TABLE IF EXISTS `notificaciones`;
CREATE TABLE `notificaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` enum('nuevo_reporte','avistamiento','encontrada','reclamo') NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `reporte_id` int DEFAULT NULL,
  `mascota_id` int DEFAULT NULL,
  `usuario_id` int NOT NULL,
  `destinatario_id` int DEFAULT NULL,
  `creado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('nuevo_reporte','Laura reportó como perdida a Kira (Husky) en Medellín - Laureles',13,13,2,'2026-11-17 07:30:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('encontrada','Laura reportó que encontró a un gato gris en Bogotá - Usaquén',12,12,2,'2026-11-16 09:00:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('avistamiento','Laura vio a Toby en Popayán - Calle 5 con carrera 6, caminando hacia el norte',6,6,2,'2026-11-16 10:40:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('encontrada','Juan reportó que encontró a Coco (Poodle) en Popayán - Parque Caldas',11,11,3,'2026-11-16 15:30:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('nuevo_reporte','Juan reportó como perdida a Simba (Criollo) en Popayán - Barrio Modelo',10,10,3,'2026-11-16 19:05:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('avistamiento','Laura vio a Max en Popayán - Barrio Bolívar, cerca de la panadería',2,2,2,'2026-11-16 20:15:00');
INSERT INTO `notificaciones` (`tipo`,`mensaje`,`reporte_id`,`mascota_id`,`usuario_id`,`creado_en`) VALUES ('reclamo','Laura cree que Coco es su mascota y quiere contactarte',11,11,2,'2026-11-17 08:05:00');


DROP TABLE IF EXISTS `novedades`;
CREATE TABLE `novedades` (
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

DROP TABLE IF EXISTS `lecturas_notificaciones`;
CREATE TABLE `lecturas_notificaciones` (
  `usuario_id` int NOT NULL,
  `ultima_id` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `lecturas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `planes`;
CREATE TABLE `planes` (
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

INSERT INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (1,'comunidad','Comunidad','Para cualquier persona que quiera ayudar',0,0,0,'["Ver todas las mascotas perdidas y encontradas", "Buscar con filtros por ciudad, raza, color y especie", "Reportar hasta 3 mascotas activas", "Notificaciones de la comunidad"]');
INSERT INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (2,'hogar','Hogar','Para familias con mascotas',9900,99000,0,'["Todo lo del plan Comunidad", "Reportes ilimitados", "Alertas prioritarias cuando alguien ve a tu mascota", "Cartel descargable para compartir en redes", "Soporte por correo"]');
INSERT INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (3,'fundacion','Fundación','Para fundaciones, refugios y rescatistas',39900,399000,1,'["Todo lo del plan Hogar", "Perfil de la organización con logo", "Hasta 100 reportes activos a la vez", "Reporte mensual de mascotas reunidas", "Insignia de fundación verificada", "Soporte prioritario por WhatsApp"]');
INSERT INTO `planes` (`id`,`codigo`,`nombre`,`publico`,`precio_mes`,`precio_anio`,`destacado`,`caracteristicas`) VALUES (4,'institucional','Institucional','Para veterinarias, alcaldías y universidades',119900,1199000,0,'["Todo lo del plan Fundación", "Reportes ilimitados y varias sedes", "Varios usuarios administradores", "Estadísticas por ciudad y por especie", "Acompañamiento para campañas de adopción"]');


DROP TABLE IF EXISTS `suscripciones`;
CREATE TABLE `suscripciones` (
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

SET FOREIGN_KEY_CHECKS=1;
