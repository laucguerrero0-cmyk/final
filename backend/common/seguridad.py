import datetime
from functools import wraps

import jwt
from flask import request, jsonify, g

from common import config


def crear_token(usuario):
    """Genera un token JWT con los datos básicos del usuario."""
    vence = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=config.HORAS_TOKEN)
    datos = {
        "id": usuario["id"],
        "usuario": usuario["usuario"],
        "rol": usuario["rol"],
        "exp": vence,
    }
    return jwt.encode(datos, config.SECRET_KEY, algorithm="HS256")


def token_requerido(roles=None):
    """
    Decorador que protege un endpoint.
    - Exige el encabezado:  Authorization: Bearer <token>
    - Si se indica roles=["admin"], solo deja pasar a esos roles.
    """
    def decorador(funcion):
        @wraps(funcion)
        def interno(*args, **kwargs):
            cabecera = request.headers.get("Authorization", "")
            if not cabecera.startswith("Bearer "):
                return jsonify(error="Falta el token. Use el encabezado Authorization: Bearer <token>"), 401
            try:
                datos = jwt.decode(cabecera[7:], config.SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify(error="El token venció. Inicie sesión de nuevo"), 401
            except jwt.InvalidTokenError:
                return jsonify(error="Token inválido"), 401

            if roles and datos["rol"] not in roles:
                return jsonify(error="No tiene permiso para esta acción"), 403

            g.usuario = datos          # datos del usuario que hace la petición
            return funcion(*args, **kwargs)
        return interno
    return decorador


def campos_faltantes(datos, campos):
    """Devuelve la lista de campos obligatorios que no llegaron."""
    return [c for c in campos if not str(datos.get(c, "")).strip()]
