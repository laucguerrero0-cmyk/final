"""
Migración automática y segura de la base de datos.

Los 3 microservicios comparten una sola base (TiDB). Las funciones nuevas (contacto, historial de
novedades y avisos dirigidos) necesitan 2 columnas y 1 tabla nuevas. En vez de pedirte que ejecutes
SQL a mano, cada servicio llama a `asegurar_esquema()` al arrancar:

  - solo AGREGA lo que falta (nunca borra ni modifica datos existentes),
  - es idempotente: si ya existe, no hace nada,
  - tolera que dos servicios arranquen a la vez durante el despliegue en Render,
  - si la base no responde al arrancar, reintenta en la siguiente petición.

Si prefieres hacerlo manualmente, el mismo cambio está en base_de_datos/migracion_novedades_contacto.sql
"""
import sys
import threading
import time

from common.db import consultar, ejecutar

CREAR_NOVEDADES = """
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

# (tabla, columna, sentencia que la agrega)
COLUMNAS = [
    ("usuarios", "telefono", "ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20) NULL AFTER correo"),
    ("notificaciones", "destinatario_id", "ALTER TABLE notificaciones ADD COLUMN destinatario_id INT NULL"),
]

_candado = threading.Lock()
_listo = False
_ultimo_intento = 0.0
ESPERA_REINTENTO = 10  # segundos entre intentos si la base no responde


def _existe_columna(tabla, columna):
    fila = consultar(
        "SELECT COUNT(*) AS n FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
        (tabla, columna), uno=True,
    )
    return fila["n"] > 0


def asegurar_esquema():
    """Crea lo que falte. Devuelve True si el esquema está completo."""
    global _listo, _ultimo_intento
    if _listo:
        return True
    with _candado:
        if _listo:
            return True
        if time.time() - _ultimo_intento < ESPERA_REINTENTO:
            return False
        _ultimo_intento = time.time()
        try:
            for tabla, columna, sentencia in COLUMNAS:
                if _existe_columna(tabla, columna):
                    continue
                try:
                    ejecutar(sentencia)
                except Exception:
                    # Otro servicio pudo haberla creado justo antes: si ya existe, todo bien
                    if not _existe_columna(tabla, columna):
                        raise
            ejecutar(CREAR_NOVEDADES)
            _listo = True
        except Exception as error:  # la app arranca igual; se reintenta en la próxima petición
            print(f"[migraciones] No se pudo actualizar la base de datos: {error}", file=sys.stderr)
    return _listo
