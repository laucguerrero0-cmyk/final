"""
Fotos guardadas en la base de datos.

Render (plan gratis) borra los archivos del servidor cada vez que se duerme o se redespliega, así que las
fotos NO pueden vivir en una carpeta. Se guardan en la tabla `fotos` y se sirven desde
GET /uploads/<nombre> del microservicio de mascotas. Para el frontend nada cambia: la URL sigue siendo
"/uploads/<nombre>".

- Se valida el CONTENIDO del archivo (JPG, PNG o WEBP), no solo la extensión que dice tener.
- El frontend ya reduce cada foto a menos de 1 MB; aquí el tope es de 5 MB (el límite de una fila de TiDB es 6 MB).
- Cada persona puede subir un número limitado de fotos por día para que nadie llene la base.
"""
import re
import uuid

from common.db import consultar, ejecutar

MAX_BYTES = 5 * 1024 * 1024
MAX_POR_DIA = 40
PATRON_URL = re.compile(r"^/uploads/[A-Za-z0-9_.-]{1,100}$")


class DemasiadasFotos(ValueError):
    """La persona superó el límite diario de fotos (se responde 429)."""


def tipo_de_imagen(datos):
    """('jpg', 'image/jpeg') según los primeros bytes del archivo, o None si no es una imagen admitida."""
    if datos[:3] == b"\xff\xd8\xff":
        return "jpg", "image/jpeg"
    if datos[:8] == b"\x89PNG\r\n\x1a\n":
        return "png", "image/png"
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "webp", "image/webp"
    return None


def guardar_foto(archivo, usuario_id, prefijo="foto"):
    """Guarda la foto en la base y devuelve su URL ('/uploads/<nombre>'). Lanza ValueError si no sirve."""
    datos = archivo.read(MAX_BYTES + 1)
    if not datos:
        raise ValueError("La foto está vacía")
    if len(datos) > MAX_BYTES:
        raise ValueError("La foto pesa más de 5 MB")
    tipo = tipo_de_imagen(datos)
    if not tipo:
        raise ValueError("La foto debe ser JPG, PNG o WEBP")

    hoy = consultar(
        "SELECT COUNT(*) AS n FROM fotos WHERE usuario_id = %s AND creado_en > (NOW() - INTERVAL 1 DAY)",
        (usuario_id,), uno=True,
    )["n"]
    if hoy >= MAX_POR_DIA:
        raise DemasiadasFotos("Subiste muchas fotos hoy. Intenta de nuevo mañana")

    extension, mime = tipo
    nombre = f"{prefijo}_{uuid.uuid4().hex[:12]}.{extension}"
    ejecutar(
        "INSERT INTO fotos (nombre, tipo, contenido, usuario_id) VALUES (%s, %s, %s, %s)",
        (nombre, mime, datos, usuario_id),
    )
    return f"/uploads/{nombre}"


def validar_foto_url(valor):
    """None si viene vacía; si no, debe ser una ruta '/uploads/...' (nunca un enlace a otro sitio)."""
    if valor is None or str(valor).strip() == "":
        return None
    texto = str(valor).strip()
    if not PATRON_URL.match(texto):
        raise ValueError("La foto no es válida")
    return texto


def foto_es_de(url, usuario_id):
    """True si la foto existe y la subió esa persona (para adjuntarla a un aviso)."""
    nombre = url.rsplit("/", 1)[-1]
    return bool(consultar(
        "SELECT 1 AS ok FROM fotos WHERE nombre = %s AND usuario_id = %s", (nombre, usuario_id), uno=True))


def borrar_foto(url):
    """Quita una foto de la base (al eliminar o reemplazar). Ignora URLs que no sean de la base."""
    if url and PATRON_URL.match(str(url)):
        ejecutar("DELETE FROM fotos WHERE nombre = %s", (url.rsplit("/", 1)[-1],))
