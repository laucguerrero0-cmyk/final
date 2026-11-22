"""
MICROSERVICIO 2: Reportes, búsqueda y notificaciones  (puerto 5002)
Reportes de mascotas perdidas o encontradas, avistamientos y el feed de notificaciones.
Todos los endpoints exigen token JWT.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, g
from flask_cors import CORS

from common.db import consultar, ejecutar
from common.seguridad import token_requerido, campos_faltantes

app = Flask(__name__)
CORS(app)                          # permite que el frontend de Vue (otro puerto) consuma esta API
app.json.ensure_ascii = False

# Consulta base: el reporte junto con los datos de su mascota y de quien lo hizo
SQL_REPORTES = (
    "SELECT r.id, r.tipo, r.estado, r.lugar, r.descripcion, r.fecha, r.usuario_id, "
    "m.id AS mascota_id, m.nombre AS mascota, m.especie, m.raza, m.color, "
    "m.descripcion AS descripcion_mascota, m.foto_url, u.nombre AS reportado_por "
    "FROM reportes r JOIN mascotas m ON m.id = r.mascota_id "
    "JOIN usuarios u ON u.id = r.usuario_id "
)


# ---------------------------------------------------------------- utilidades
def primer_nombre():
    """Primer nombre de quien hace la petición (para armar los mensajes)."""
    fila = consultar("SELECT nombre FROM usuarios WHERE id = %s", (g.usuario["id"],), uno=True)
    return fila["nombre"].split()[0] if fila else g.usuario["usuario"]


def describir(m):
    """Texto corto de una mascota: 'Max (Pastor)' o 'un gato gris' si no tiene nombre."""
    if m["nombre"] == "Sin nombre":
        return "un " + " ".join(x for x in (m["especie"].lower(), (m["color"] or "").lower()) if x)
    return f"{m['nombre']} ({m['raza'] or m['especie']})"


def notificar(tipo, mensaje, reporte_id, mascota_id):
    """Guarda un aviso en el feed de notificaciones."""
    ejecutar(
        "INSERT INTO notificaciones (tipo, mensaje, reporte_id, mascota_id, usuario_id) "
        "VALUES (%s, %s, %s, %s, %s)",
        (tipo, mensaje[:255], reporte_id, mascota_id, g.usuario["id"]),
    )


# ------------------------------------------------------------------ reportes
# 1. POST /reportes  -> crear reporte de pérdida o hallazgo
@app.route("/reportes", methods=["POST"])
@token_requerido()
def crear_reporte():
    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["mascota_id", "tipo", "lugar"])
    if falta:
        return jsonify(error="Faltan campos obligatorios", campos=falta), 400
    if datos["tipo"] not in ("perdida", "encontrada"):
        return jsonify(error="El tipo debe ser 'perdida' o 'encontrada'"), 400
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (datos["mascota_id"],), uno=True)
    if not mascota:
        return jsonify(error="La mascota indicada no existe"), 404

    nuevo_id = ejecutar(
        "INSERT INTO reportes (mascota_id, usuario_id, tipo, lugar, descripcion) VALUES (%s, %s, %s, %s, %s)",
        (datos["mascota_id"], g.usuario["id"], datos["tipo"], datos["lugar"], datos.get("descripcion")),
    )
    autor = primer_nombre()
    if datos["tipo"] == "perdida":
        texto = f"{autor} reportó como perdida a {describir(mascota)} en {datos['lugar']}"
        notificar("nuevo_reporte", texto, nuevo_id, mascota["id"])
    else:
        texto = f"{autor} reportó que encontró a {describir(mascota)} en {datos['lugar']}"
        notificar("encontrada", texto, nuevo_id, mascota["id"])
    return jsonify(mensaje="Reporte creado correctamente", id=nuevo_id), 201


# 2. GET /reportes  -> listar todos
@app.route("/reportes", methods=["GET"])
@token_requerido()
def listar_reportes():
    return jsonify(consultar(SQL_REPORTES + "ORDER BY r.id"))


# 3. GET /reportes/buscar  -> búsqueda con filtros (todos opcionales y combinables)
#    ?q=nombre &ciudad= &lugar= &especie= &raza= &color= &tipo= &estado=
@app.route("/reportes/buscar", methods=["GET"])
@token_requerido()
def buscar_reportes():
    a = request.args
    condiciones, valores = [], []
    if a.get("q"):
        condiciones.append("m.nombre LIKE %s")
        valores.append("%" + a["q"] + "%")
    if a.get("ciudad"):
        condiciones.append("r.lugar LIKE %s")        # el lugar se guarda como 'Ciudad - Barrio'
        valores.append(a["ciudad"] + "%")
    if a.get("lugar"):
        condiciones.append("r.lugar LIKE %s")
        valores.append("%" + a["lugar"] + "%")
    if a.get("especie"):
        condiciones.append("m.especie = %s")
        valores.append(a["especie"])
    if a.get("raza"):
        condiciones.append("m.raza LIKE %s")
        valores.append("%" + a["raza"] + "%")
    if a.get("color"):
        condiciones.append("m.color = %s")
        valores.append(a["color"])
    if a.get("estado"):
        condiciones.append("r.estado = %s")
        valores.append(a["estado"])
    if a.get("tipo"):
        condiciones.append("r.tipo = %s")
        valores.append(a["tipo"])

    where = "WHERE " + " AND ".join(condiciones) + " " if condiciones else ""
    resultados = consultar(SQL_REPORTES + where + "ORDER BY r.fecha DESC, r.id DESC", tuple(valores))
    return jsonify(total=len(resultados), resultados=resultados)


# 4. GET /reportes/filtros  -> valores disponibles para armar los desplegables de filtros
@app.route("/reportes/filtros", methods=["GET"])
@token_requerido()
def valores_filtros():
    filas = consultar(
        "SELECT r.lugar, m.especie, m.raza, m.color FROM reportes r JOIN mascotas m ON m.id = r.mascota_id"
    )
    ciudades = {f["lugar"].split(" - ")[0].strip() for f in filas}
    return jsonify(
        ciudades=sorted(ciudades),
        especies=sorted({f["especie"] for f in filas}),
        razas=sorted({f["raza"] for f in filas if f["raza"]}),
        colores=sorted({f["color"] for f in filas if f["color"]}),
    )


# 5. GET /reportes/resumen  -> números para el Home
@app.route("/reportes/resumen", methods=["GET"])
@token_requerido()
def resumen():
    def contar(condicion):
        return consultar("SELECT COUNT(*) AS n FROM reportes WHERE " + condicion, uno=True)["n"]
    return jsonify(
        perdidas=contar("tipo = 'perdida' AND estado = 'abierto'"),
        encontradas=contar("tipo = 'encontrada'"),
        reunidas=contar("tipo = 'perdida' AND estado = 'resuelto'"),
    )


# 6. GET /reportes/<id>  -> consultar un reporte
@app.route("/reportes/<int:id>", methods=["GET"])
@token_requerido()
def consultar_reporte(id):
    reporte = consultar(SQL_REPORTES + "WHERE r.id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    return jsonify(reporte)


# 7. PUT /reportes/<id>/estado  -> cambiar el estado (abierto / resuelto)
@app.route("/reportes/<int:id>/estado", methods=["PUT"])
@token_requerido()
def cambiar_estado(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if g.usuario["rol"] != "admin" and reporte["usuario_id"] != g.usuario["id"]:
        return jsonify(error="Solo quien creó el reporte o un administrador puede cambiar su estado"), 403

    datos = request.get_json(silent=True) or {}
    if datos.get("estado") not in ("abierto", "resuelto"):
        return jsonify(error="El estado debe ser 'abierto' o 'resuelto'"), 400
    ejecutar("UPDATE reportes SET estado = %s WHERE id = %s", (datos["estado"], id))
    return jsonify(mensaje="Estado del reporte actualizado", estado=datos["estado"])


# 8. PUT /reportes/<id>/encontrada  -> CUALQUIER usuario avisa que encontró la mascota
#    (botón "¡La encontré!"). Cierra el reporte de pérdida, deja un reporte 'encontrada'
#    a nombre de quien la halló y avisa a la comunidad.
@app.route("/reportes/<int:id>/encontrada", methods=["PUT"])
@token_requerido()
def marcar_encontrada(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if reporte["tipo"] != "perdida":
        return jsonify(error="Solo se pueden marcar como encontradas las mascotas reportadas como perdidas"), 400
    if reporte["estado"] == "resuelto":
        return jsonify(error="Esta mascota ya fue marcada como encontrada"), 409

    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["lugar"])
    if falta:
        return jsonify(error="Indica dónde la encontraste", campos=falta), 400

    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    ejecutar("UPDATE reportes SET estado = 'resuelto' WHERE id = %s", (id,))
    nuevo_id = ejecutar(
        "INSERT INTO reportes (mascota_id, usuario_id, tipo, lugar, descripcion, estado) "
        "VALUES (%s, %s, 'encontrada', %s, %s, 'resuelto')",
        (reporte["mascota_id"], g.usuario["id"], datos["lugar"], datos.get("descripcion")),
    )
    notificar("encontrada", f"¡{mascota['nombre']} fue encontrada! {primer_nombre()} la encontró en {datos['lugar']}",
              nuevo_id, mascota["id"])
    return jsonify(mensaje="¡Gracias! La mascota quedó marcada como encontrada", id=nuevo_id)


# 9. POST /reportes/<id>/avistamiento  -> "la vi por aquí" (sin cerrar el reporte)
@app.route("/reportes/<int:id>/avistamiento", methods=["POST"])
@token_requerido()
def registrar_avistamiento(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if reporte["tipo"] != "perdida" or reporte["estado"] != "abierto":
        return jsonify(error="Solo se pueden avistar mascotas con un reporte de pérdida abierto"), 400
    datos = request.get_json(silent=True) or {}
    if campos_faltantes(datos, ["lugar"]):
        return jsonify(error="Indica dónde la viste", campos=["lugar"]), 400

    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    texto = f"{primer_nombre()} vio a {mascota['nombre']} en {datos['lugar']}"
    if datos.get("descripcion"):
        texto += f", {datos['descripcion']}"
    notificar("avistamiento", texto, id, mascota["id"])
    return jsonify(mensaje="¡Gracias! Avisamos a quien la está buscando"), 201


# 10. POST /reportes/<id>/reclamar  -> "creo que es mi mascota" (sobre un reporte de hallazgo)
@app.route("/reportes/<int:id>/reclamar", methods=["POST"])
@token_requerido()
def reclamar_mascota(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if reporte["tipo"] != "encontrada" or reporte["estado"] != "abierto":
        return jsonify(error="Solo se puede reclamar una mascota con un reporte de hallazgo abierto"), 400
    if reporte["usuario_id"] == g.usuario["id"]:
        return jsonify(error="Este reporte es tuyo"), 400

    datos = request.get_json(silent=True) or {}
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    texto = f"{primer_nombre()} cree que {describir(mascota)} es su mascota y quiere contactarte"
    if datos.get("descripcion"):
        texto += f": {datos['descripcion']}"
    notificar("reclamo", texto, id, mascota["id"])
    return jsonify(mensaje="Le avisamos a quien la encontró. ¡Pronto se pondrá en contacto!"), 201


# ------------------------------------------------------------ notificaciones
def _ultima_leida():
    fila = consultar("SELECT ultima_id FROM lecturas_notificaciones WHERE usuario_id = %s",
                     (g.usuario["id"],), uno=True)
    return fila["ultima_id"] if fila else 0


# 11. GET /notificaciones  -> feed de la comunidad (lo más reciente primero)
@app.route("/notificaciones", methods=["GET"])
@token_requerido()
def listar_notificaciones():
    ultima = _ultima_leida()
    filas = consultar(
        "SELECT n.id, n.tipo, n.mensaje, n.reporte_id, n.mascota_id, n.creado_en, "
        "n.usuario_id AS autor_id, m.nombre AS mascota, m.especie, m.color, m.foto_url, "
        "rp.usuario_id AS dueno_reporte "
        "FROM notificaciones n "
        "LEFT JOIN mascotas m ON m.id = n.mascota_id "
        "LEFT JOIN reportes rp ON rp.id = n.reporte_id "
        "ORDER BY n.id DESC LIMIT 50"
    )
    yo = g.usuario["id"]
    for f in filas:
        propia = f["autor_id"] == yo
        f["leida"] = propia or f["id"] <= ultima
        f["sobre_mi_reporte"] = (f["dueno_reporte"] == yo) and not propia
        f["es_mia"] = propia
        del f["dueno_reporte"]
    return jsonify(no_leidas=sum(1 for f in filas if not f["leida"]), notificaciones=filas)


# 12. GET /notificaciones/resumen  -> solo el contador (lo consulta la campana de la barra)
@app.route("/notificaciones/resumen", methods=["GET"])
@token_requerido()
def resumen_notificaciones():
    n = consultar("SELECT COUNT(*) AS n FROM notificaciones WHERE id > %s AND usuario_id <> %s",
                  (_ultima_leida(), g.usuario["id"]), uno=True)["n"]
    return jsonify(no_leidas=n)


# 13. PUT /notificaciones/leer  -> marcar todo como leído
@app.route("/notificaciones/leer", methods=["PUT"])
@token_requerido()
def marcar_leidas():
    ultimo = consultar("SELECT MAX(id) AS m FROM notificaciones", uno=True)["m"] or 0
    existe = consultar("SELECT usuario_id FROM lecturas_notificaciones WHERE usuario_id = %s",
                       (g.usuario["id"],), uno=True)
    if existe:
        ejecutar("UPDATE lecturas_notificaciones SET ultima_id = %s WHERE usuario_id = %s",
                 (ultimo, g.usuario["id"]))
    else:
        ejecutar("INSERT INTO lecturas_notificaciones (usuario_id, ultima_id) VALUES (%s, %s)",
                 (g.usuario["id"], ultimo))
    return jsonify(mensaje="Notificaciones marcadas como leídas", no_leidas=0)


if __name__ == "__main__":
    app.run(port=5002, debug=False)
