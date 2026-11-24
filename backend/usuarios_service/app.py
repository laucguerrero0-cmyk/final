"""
MICROSERVICIO 3: Usuarios y autenticación  (puerto 5003)
Registra usuarios, hace el login y entrega el token JWT.
"""
import datetime
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from pymysql.err import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from common.contacto import limpiar_telefono
from common.db import consultar, ejecutar
from common.migraciones import asegurar_esquema
from common.seguridad import crear_token, token_requerido, campos_faltantes

app = Flask(__name__)
CORS(app)                          # permite que el frontend de Vue (otro puerto) consuma esta API
app.json.ensure_ascii = False      # para ver bien las tildes en Postman

# Agrega (sin borrar nada) las columnas/tablas nuevas de la base compartida; ver common/migraciones.py
asegurar_esquema()


@app.before_request
def _esquema_listo():
    asegurar_esquema()             # si la base no respondió al arrancar, reintenta aquí


CAMPOS_PUBLICOS = "id, nombre, usuario, correo, telefono, rol, creado_en"


# 1. POST /auth/registro  (público: es la puerta de entrada)
@app.route("/auth/registro", methods=["POST"])
def registro():
    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["nombre", "usuario", "password"])
    if falta:
        return jsonify(error="Faltan campos obligatorios", campos=falta), 400
    try:
        telefono = limpiar_telefono(datos.get("telefono"))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    try:
        nuevo_id = ejecutar(
            "INSERT INTO usuarios (nombre, usuario, correo, telefono, password_hash, rol) "
            "VALUES (%s, %s, %s, %s, %s, 'usuario')",
            (datos["nombre"], datos["usuario"], datos.get("correo"), telefono,
             generate_password_hash(datos["password"], method="pbkdf2:sha256")),
        )
    except IntegrityError:
        return jsonify(error="Ese nombre de usuario ya existe"), 409
    return jsonify(mensaje="Usuario registrado correctamente", id=nuevo_id), 201


# 2. POST /auth/login  (público: aquí se obtiene el token)
@app.route("/auth/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["usuario", "password"])
    if falta:
        return jsonify(error="Faltan campos obligatorios", campos=falta), 400

    usuario = consultar("SELECT * FROM usuarios WHERE usuario = %s", (datos["usuario"],), uno=True)
    if not usuario or not check_password_hash(usuario["password_hash"], datos["password"]):
        return jsonify(error="Usuario o contraseña incorrectos"), 401

    return jsonify(
        mensaje="Inicio de sesión correcto",
        token=crear_token(usuario),
        usuario={"id": usuario["id"], "nombre": usuario["nombre"], "rol": usuario["rol"],
                 "telefono": usuario.get("telefono")},
    )


# 3. GET /usuarios  (solo administrador)
@app.route("/usuarios", methods=["GET"])
@token_requerido(roles=["admin"])
def listar_usuarios():
    return jsonify(consultar(f"SELECT {CAMPOS_PUBLICOS} FROM usuarios ORDER BY id"))


# 4. GET /usuarios/<id>  (el mismo usuario o un administrador)
@app.route("/usuarios/<int:id>", methods=["GET"])
@token_requerido()
def consultar_usuario(id):
    if g.usuario["id"] != id and g.usuario["rol"] != "admin":
        return jsonify(error="Solo puede consultar su propio usuario"), 403
    usuario = consultar(f"SELECT {CAMPOS_PUBLICOS} FROM usuarios WHERE id = %s", (id,), uno=True)
    if not usuario:
        return jsonify(error="Usuario no encontrado"), 404
    return jsonify(usuario)


# 5. PUT /usuarios/<id>  (el mismo usuario o un administrador)
@app.route("/usuarios/<int:id>", methods=["PUT"])
@token_requerido()
def actualizar_usuario(id):
    if g.usuario["id"] != id and g.usuario["rol"] != "admin":
        return jsonify(error="Solo puede modificar su propio usuario"), 403
    actual = consultar("SELECT * FROM usuarios WHERE id = %s", (id,), uno=True)
    if not actual:
        return jsonify(error="Usuario no encontrado"), 404

    datos = request.get_json(silent=True) or {}
    nuevo_hash = actual["password_hash"]
    if datos.get("password"):
        nuevo_hash = generate_password_hash(datos["password"], method="pbkdf2:sha256")

    telefono = actual.get("telefono")
    if "telefono" in datos:                       # '' borra el teléfono; si no viene, se conserva
        try:
            telefono = limpiar_telefono(datos["telefono"])
        except ValueError as e:
            return jsonify(error=str(e)), 400

    ejecutar(
        "UPDATE usuarios SET nombre = %s, correo = %s, telefono = %s, password_hash = %s WHERE id = %s",
        (datos.get("nombre", actual["nombre"]), datos.get("correo", actual["correo"]), telefono, nuevo_hash, id),
    )
    return jsonify(mensaje="Usuario actualizado correctamente")


# ---------------------------------------------------------------- planes
# 6. GET /planes  (público: es la vitrina de precios)
@app.route("/planes", methods=["GET"])
def listar_planes():
    planes = consultar("SELECT * FROM planes ORDER BY precio_mes")
    for p in planes:
        p["caracteristicas"] = json.loads(p["caracteristicas"])
        p["destacado"] = bool(p["destacado"])
    return jsonify(planes)


SQL_SUSCRIPCION = (
    "SELECT s.id, s.periodo, s.organizacion, s.estado, s.creado_en, s.vence_en, "
    "p.id AS plan_id, p.codigo, p.nombre AS plan, p.precio_mes, p.precio_anio "
    "FROM suscripciones s JOIN planes p ON p.id = s.plan_id "
)


# 7. POST /suscripciones  -> contratar un plan (el pago es simulado: no se piden datos de tarjeta)
@app.route("/suscripciones", methods=["POST"])
@token_requerido()
def suscribirse():
    datos = request.get_json(silent=True) or {}
    plan = consultar("SELECT * FROM planes WHERE id = %s", (datos.get("plan_id"),), uno=True)
    if not plan:
        return jsonify(error="El plan indicado no existe"), 404
    if datos.get("periodo") not in ("mensual", "anual"):
        return jsonify(error="El periodo debe ser 'mensual' o 'anual'"), 400
    organizacion = (datos.get("organizacion") or "").strip() or None
    if plan["codigo"] in ("fundacion", "institucional") and not organizacion:
        return jsonify(error="Indica el nombre de tu fundación u organización"), 400

    vence = None
    if plan["precio_mes"] > 0:
        dias = 30 if datos["periodo"] == "mensual" else 365
        vence = (datetime.datetime.now() + datetime.timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")

    # una persona solo tiene una suscripción activa: la anterior se cancela
    ejecutar("UPDATE suscripciones SET estado = 'cancelada' WHERE usuario_id = %s AND estado = 'activa'",
             (g.usuario["id"],))
    nuevo_id = ejecutar(
        "INSERT INTO suscripciones (usuario_id, plan_id, periodo, organizacion, vence_en) "
        "VALUES (%s, %s, %s, %s, %s)",
        (g.usuario["id"], plan["id"], datos["periodo"], organizacion, vence),
    )
    return jsonify(mensaje=f"Ya tienes el plan {plan['nombre']}", id=nuevo_id), 201


# 8. GET /suscripciones/mia  -> plan activo de quien hace la petición (o null)
@app.route("/suscripciones/mia", methods=["GET"])
@token_requerido()
def mi_suscripcion():
    fila = consultar(SQL_SUSCRIPCION + "WHERE s.usuario_id = %s AND s.estado = 'activa' ORDER BY s.id DESC",
                     (g.usuario["id"],), uno=True)
    return jsonify(suscripcion=fila)


# 9. DELETE /suscripciones/mia  -> cancelar el plan (vuelve al plan gratuito)
@app.route("/suscripciones/mia", methods=["DELETE"])
@token_requerido()
def cancelar_suscripcion():
    ejecutar("UPDATE suscripciones SET estado = 'cancelada' WHERE usuario_id = %s AND estado = 'activa'",
             (g.usuario["id"],))
    return jsonify(mensaje="Suscripción cancelada")


if __name__ == "__main__":
    app.run(port=5003, debug=False)
