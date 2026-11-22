"""
MICROSERVICIO 1: Gestión de mascotas  (puerto 5001)
CRUD de las mascotas. Todos los endpoints exigen token JWT.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid

from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS

from common.db import consultar, ejecutar
from common.seguridad import token_requerido, campos_faltantes

app = Flask(__name__)
CORS(app)                          # permite que el frontend de Vue (otro puerto) consuma esta API
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024        # fotos de máximo 4 MB

CARPETA_FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
EXTENSIONES = {"jpg", "jpeg", "png", "webp"}
os.makedirs(CARPETA_FOTOS, exist_ok=True)


def puede_modificar(mascota):
    """Solo el dueño del registro o un administrador pueden cambiarlo."""
    return g.usuario["rol"] == "admin" or mascota["usuario_id"] == g.usuario["id"]


# 1. POST /mascotas  -> registrar una mascota
@app.route("/mascotas", methods=["POST"])
@token_requerido()
def registrar_mascota():
    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["nombre", "especie"])
    if falta:
        return jsonify(error="Faltan campos obligatorios", campos=falta), 400
    nuevo_id = ejecutar(
        "INSERT INTO mascotas (nombre, especie, raza, color, descripcion, foto_url, usuario_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (datos["nombre"], datos["especie"], datos.get("raza"), datos.get("color"),
         datos.get("descripcion"), datos.get("foto_url"), g.usuario["id"]),
    )
    return jsonify(mensaje="Mascota registrada correctamente", id=nuevo_id), 201


# 2. GET /mascotas  -> listar (opcional: ?especie=Perro)
@app.route("/mascotas", methods=["GET"])
@token_requerido()
def listar_mascotas():
    especie = request.args.get("especie")
    if especie:
        return jsonify(consultar("SELECT * FROM mascotas WHERE especie = %s ORDER BY id", (especie,)))
    return jsonify(consultar("SELECT * FROM mascotas ORDER BY id"))


# 3. GET /mascotas/<id>  -> consultar una
@app.route("/mascotas/<int:id>", methods=["GET"])
@token_requerido()
def consultar_mascota(id):
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (id,), uno=True)
    if not mascota:
        return jsonify(error="Mascota no encontrada"), 404
    return jsonify(mascota)


# 4. PUT /mascotas/<id>  -> actualizar
@app.route("/mascotas/<int:id>", methods=["PUT"])
@token_requerido()
def actualizar_mascota(id):
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (id,), uno=True)
    if not mascota:
        return jsonify(error="Mascota no encontrada"), 404
    if not puede_modificar(mascota):
        return jsonify(error="Solo el dueño del registro o un administrador puede modificarlo"), 403

    datos = request.get_json(silent=True) or {}
    ejecutar(
        "UPDATE mascotas SET nombre = %s, especie = %s, raza = %s, color = %s, descripcion = %s, foto_url = %s WHERE id = %s",
        (datos.get("nombre", mascota["nombre"]), datos.get("especie", mascota["especie"]),
         datos.get("raza", mascota["raza"]), datos.get("color", mascota["color"]),
         datos.get("descripcion", mascota["descripcion"]),
         datos.get("foto_url", mascota["foto_url"]), id),
    )
    return jsonify(mensaje="Mascota actualizada correctamente")


# 5. DELETE /mascotas/<id>  -> eliminar
@app.route("/mascotas/<int:id>", methods=["DELETE"])
@token_requerido()
def eliminar_mascota(id):
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (id,), uno=True)
    if not mascota:
        return jsonify(error="Mascota no encontrada"), 404
    if not puede_modificar(mascota):
        return jsonify(error="Solo el dueño del registro o un administrador puede eliminarlo"), 403
    ejecutar("DELETE FROM mascotas WHERE id = %s", (id,))
    return jsonify(mensaje="Mascota eliminada correctamente")


# 6. POST /mascotas/<id>/foto  -> subir la foto (multipart/form-data, campo "foto")
@app.route("/mascotas/<int:id>/foto", methods=["POST"])
@token_requerido()
def subir_foto(id):
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (id,), uno=True)
    if not mascota:
        return jsonify(error="Mascota no encontrada"), 404
    if not puede_modificar(mascota):
        return jsonify(error="Solo el dueño del registro o un administrador puede cambiar la foto"), 403
    archivo = request.files.get("foto")
    if not archivo or not archivo.filename:
        return jsonify(error="Falta el archivo (campo 'foto')"), 400
    extension = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if extension not in EXTENSIONES:
        return jsonify(error="La foto debe ser JPG, PNG o WEBP"), 400

    nombre = f"mascota_{id}_{uuid.uuid4().hex[:8]}.{extension}"
    archivo.save(os.path.join(CARPETA_FOTOS, nombre))
    ejecutar("UPDATE mascotas SET foto_url = %s WHERE id = %s", (f"/uploads/{nombre}", id))
    return jsonify(mensaje="Foto guardada", foto_url=f"/uploads/{nombre}")


# 7. GET /uploads/<archivo>  -> servir las fotos (público: las usa la etiqueta <img>)
@app.route("/uploads/<path:archivo>", methods=["GET"])
def ver_foto(archivo):
    return send_from_directory(CARPETA_FOTOS, archivo)


@app.errorhandler(413)
def foto_muy_grande(_):
    return jsonify(error="La foto pesa más de 4 MB"), 413


if __name__ == "__main__":
    app.run(port=5001, debug=False)
