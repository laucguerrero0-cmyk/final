"""
MICROSERVICIO 1: Gestión de mascotas  (puerto 5001)
CRUD de las mascotas. Todos los endpoints exigen token JWT.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response, request, jsonify, g, send_from_directory
from flask_cors import CORS

from common.contacto import capitalizar, texto_o_none
from common.db import consultar, ejecutar
from common.fotos import DemasiadasFotos, borrar_foto, guardar_foto, validar_foto_url
from common.migraciones import asegurar_esquema
from common.seguridad import token_requerido, campos_faltantes

app = Flask(__name__)
CORS(app)                          # permite que el frontend de Vue (otro puerto) consuma esta API
app.json.ensure_ascii = False
# El frontend reduce cada foto antes de subirla (queda en menos de 1 MB), aunque la original pese 20 MB.
# Este límite es la red de seguridad: lo que llegue sin reducir y pase de 5 MB se rechaza.
MAX_FOTO_MB = 5
app.config["MAX_CONTENT_LENGTH"] = (MAX_FOTO_MB + 1) * 1024 * 1024    # + margen del formulario multipart

# Las fotos viven en la base de datos (ver common/fotos.py). Esta carpeta solo sirve para las fotos
# antiguas que se hubieran guardado como archivo antes de este cambio.
CARPETA_FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

# Agrega (sin borrar nada) las tablas y columnas nuevas de la base compartida; ver common/migraciones.py
asegurar_esquema()


@app.before_request
def _esquema_listo():
    asegurar_esquema()             # si la base no respondió al arrancar, reintenta aquí


def puede_modificar(mascota):
    """Solo el dueño del registro o un administrador pueden cambiarlo."""
    return g.usuario["rol"] == "admin" or mascota["usuario_id"] == g.usuario["id"]


# Especie, raza y color son texto LIBRE (cada persona escribe lo que necesite: 'Conejo', 'Mestizo', 'Tricolor'...).
# Se limpian los espacios, se pone la primera letra en mayúscula y se valida el largo que admite la base.
LIMITES = {"nombre": 80, "especie": 40, "raza": 60, "color": 40, "descripcion": 255}
CON_MAYUSCULA = ("especie", "raza", "color")


def limpiar_campo(campo, valor):
    texto = texto_o_none(valor, LIMITES[campo])
    return capitalizar(texto) if campo in CON_MAYUSCULA else texto


# 1. POST /mascotas  -> registrar una mascota
@app.route("/mascotas", methods=["POST"])
@token_requerido()
def registrar_mascota():
    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["nombre", "especie"])
    if falta:
        return jsonify(error="Faltan campos obligatorios", campos=falta), 400
    try:
        limpios = {c: limpiar_campo(c, datos.get(c)) for c in LIMITES}
        foto_url = validar_foto_url(datos.get("foto_url"))
    except ValueError as e:
        return jsonify(error=f"Revisa los datos de la mascota: {e}"), 400
    nuevo_id = ejecutar(
        "INSERT INTO mascotas (nombre, especie, raza, color, descripcion, foto_url, usuario_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (limpios["nombre"], limpios["especie"], limpios["raza"], limpios["color"],
         limpios["descripcion"], foto_url, g.usuario["id"]),
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
    try:
        limpios = {c: (limpiar_campo(c, datos[c]) if c in datos else mascota[c]) for c in LIMITES}
        foto_url = validar_foto_url(datos["foto_url"]) if "foto_url" in datos else mascota["foto_url"]
    except ValueError as e:
        return jsonify(error=f"Revisa los datos de la mascota: {e}"), 400
    if not limpios["nombre"] or not limpios["especie"]:
        return jsonify(error="El nombre y la especie no pueden quedar vacíos"), 400
    ejecutar(
        "UPDATE mascotas SET nombre = %s, especie = %s, raza = %s, color = %s, descripcion = %s, foto_url = %s WHERE id = %s",
        (limpios["nombre"], limpios["especie"], limpios["raza"], limpios["color"], limpios["descripcion"],
         foto_url, id),
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
    borrar_foto(mascota["foto_url"])
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
    try:
        foto_url = guardar_foto(archivo, g.usuario["id"], prefijo=f"mascota_{id}")
    except DemasiadasFotos as e:
        return jsonify(error=str(e)), 429
    except ValueError as e:
        return jsonify(error=str(e)), 400
    ejecutar("UPDATE mascotas SET foto_url = %s WHERE id = %s", (foto_url, id))
    borrar_foto(mascota["foto_url"])        # la foto anterior ya no se necesita
    return jsonify(mensaje="Foto guardada", foto_url=foto_url)


# 7. GET /uploads/<archivo>  -> servir las fotos (público: las usa la etiqueta <img>)
#    Los nombres son únicos y nunca cambian de contenido, por eso el navegador puede guardarlas mucho tiempo.
@app.route("/uploads/<path:archivo>", methods=["GET"])
def ver_foto(archivo):
    foto = consultar("SELECT tipo, contenido FROM fotos WHERE nombre = %s", (archivo,), uno=True)
    if foto:
        return Response(foto["contenido"], mimetype=foto["tipo"], headers={
            "Cache-Control": "public, max-age=604800, immutable",
            "X-Content-Type-Options": "nosniff",
        })
    return send_from_directory(CARPETA_FOTOS, archivo)      # fotos antiguas guardadas como archivo (404 si no están)


@app.errorhandler(413)
def foto_muy_grande(_):
    return jsonify(error=f"La foto pesa más de {MAX_FOTO_MB} MB. Prueba con otra o con menos calidad"), 413


if __name__ == "__main__":
    app.run(port=5001, debug=False)
