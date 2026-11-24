"""
MICROSERVICIO 2: Reportes, búsqueda, historial y notificaciones  (puerto 5002)
Reportes de mascotas perdidas o encontradas, novedades de cada reporte (avistamientos, avisos de
hallazgo, reclamos), contacto entre personas y el feed de notificaciones.
Todos los endpoints exigen token JWT.
"""
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, g
from flask_cors import CORS

from common.contacto import texto_o_none
from common.db import consultar, ejecutar
from common.migraciones import asegurar_esquema
from common.seguridad import token_requerido, campos_faltantes

app = Flask(__name__)
CORS(app)                          # permite que el frontend de Vue (otro puerto) consuma esta API
app.json.ensure_ascii = False

# Agrega (sin borrar nada) las columnas/tablas nuevas de la base compartida; ver common/migraciones.py
asegurar_esquema()


@app.before_request
def _esquema_listo():
    asegurar_esquema()             # si la base no respondió al arrancar, reintenta aquí


# Consulta base: el reporte junto con los datos de su mascota, de quien lo hizo y cuántas novedades tiene
SQL_REPORTES = (
    "SELECT r.id, r.tipo, r.estado, r.lugar, r.descripcion, r.fecha, r.usuario_id, "
    "m.id AS mascota_id, m.nombre AS mascota, m.especie, m.raza, m.color, "
    "m.descripcion AS descripcion_mascota, m.foto_url, u.nombre AS reportado_por, "
    "(SELECT COUNT(*) FROM novedades n WHERE n.reporte_id = r.id) AS novedades_total, "
    "(SELECT COUNT(*) FROM novedades n WHERE n.reporte_id = r.id "
    " AND n.tipo IN ('hallazgo', 'reclamo') AND n.estado = 'abierta') AS por_revisar "
    "FROM reportes r JOIN mascotas m ON m.id = r.mascota_id "
    "JOIN usuarios u ON u.id = r.usuario_id "
)

FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


class DatoInvalido(Exception):
    """Un dato enviado no es válido: se responde 400 con el mensaje."""


@app.errorhandler(DatoInvalido)
def _dato_invalido(e):
    return jsonify(error=str(e)), 400


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


def titulo_mascota(m):
    """'Max' o 'Gato sin nombre'."""
    return f"{m['especie']} sin nombre" if m["nombre"] == "Sin nombre" else m["nombre"]


def leer_texto(datos, campo, maximo, nombre):
    """Texto opcional, sin espacios de más y con el largo que admite la base."""
    try:
        return texto_o_none(datos.get(campo), maximo)
    except ValueError:
        raise DatoInvalido(f"{nombre} no puede tener más de {maximo} caracteres")


def leer_si_no(datos, campo, por_defecto):
    valor = datos.get(campo, por_defecto)
    if isinstance(valor, str):
        return valor.strip().lower() in ("1", "true", "si", "sí")
    return bool(valor)


def texto_hace(minutos):
    """15 -> 'hace 15 min', 180 -> 'hace 3 h', 0 -> 'ahora mismo'."""
    if not minutos:
        return "ahora mismo"
    if minutos < 60:
        return f"hace {minutos} min"
    if minutos < 1440:
        return f"hace {minutos // 60} h"
    dias = minutos // 1440
    return "hace 1 día" if dias == 1 else f"hace {dias} días"


def momento_visto(creado_en, hace_minutos):
    """Cuándo ocurrió lo que se avisó: la hora del aviso menos los minutos que dijo la persona."""
    if not creado_en or not hace_minutos:
        return creado_en
    base = datetime.datetime.strptime(creado_en, FORMATO_FECHA)
    return (base - datetime.timedelta(minutes=hace_minutos)).strftime(FORMATO_FECHA)


def es_dueno_o_admin(reporte):
    return g.usuario["rol"] == "admin" or reporte["usuario_id"] == g.usuario["id"]


def contacto_de(usuario_id):
    """Datos para llamar o escribir a una persona (None si no dejó ninguno)."""
    u = consultar("SELECT nombre, telefono, correo FROM usuarios WHERE id = %s", (usuario_id,), uno=True)
    if not u:
        return None
    return {"nombre": u["nombre"], "telefono": u["telefono"] or None, "correo": u["correo"] or None}


def notificar(tipo, mensaje, reporte_id, mascota_id, destinatario_id=None):
    """
    Guarda un aviso en el feed de notificaciones.
    Con `destinatario_id` el aviso es PRIVADO (solo lo ven esa persona y quien lo generó);
    sin él es un aviso de toda la comunidad.
    """
    ejecutar(
        "INSERT INTO notificaciones (tipo, mensaje, reporte_id, mascota_id, usuario_id, destinatario_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (tipo, mensaje[:255], reporte_id, mascota_id, g.usuario["id"], destinatario_id),
    )


def registrar_novedad(reporte, tipo, lugar=None, descripcion=None, condicion=None,
                      hace_minutos=None, compartir_contacto=False, estado="abierta"):
    """Anota una novedad en el historial del reporte."""
    return ejecutar(
        "INSERT INTO novedades (reporte_id, mascota_id, usuario_id, tipo, estado, lugar, descripcion, "
        "condicion, hace_minutos, compartir_contacto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (reporte["id"], reporte["mascota_id"], g.usuario["id"], tipo, estado, lugar, descripcion,
         condicion, hace_minutos, 1 if compartir_contacto else 0),
    )


def agregar_ultimo_avistamiento(filas):
    """A cada reporte de pérdida le suma dónde y cuándo la vieron por última vez."""
    ids = [f["id"] for f in filas if f["tipo"] == "perdida"]
    ultimos = {}
    if ids:
        marcas = ",".join(["%s"] * len(ids))
        avistamientos = consultar(
            "SELECT reporte_id, lugar, hace_minutos, creado_en FROM novedades "
            "WHERE tipo = 'avistamiento' AND reporte_id IN (" + marcas + ") ORDER BY id DESC",
            tuple(ids),
        )
        for a in avistamientos:
            ultimos.setdefault(a["reporte_id"], a)         # el primero de cada reporte es el más reciente
    for f in filas:
        a = ultimos.get(f["id"])
        f["ultimo_avistamiento"] = (
            {"lugar": a["lugar"], "visto_en": momento_visto(a["creado_en"], a["hace_minutos"])} if a else None
        )
    return filas


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
    lugar = leer_texto(datos, "lugar", 120, "El lugar")
    descripcion = leer_texto(datos, "descripcion", 255, "La descripción")
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (datos["mascota_id"],), uno=True)
    if not mascota:
        return jsonify(error="La mascota indicada no existe"), 404

    nuevo_id = ejecutar(
        "INSERT INTO reportes (mascota_id, usuario_id, tipo, lugar, descripcion) VALUES (%s, %s, %s, %s, %s)",
        (datos["mascota_id"], g.usuario["id"], datos["tipo"], lugar, descripcion),
    )
    autor = primer_nombre()
    if datos["tipo"] == "perdida":
        texto = f"{autor} reportó como perdida a {describir(mascota)} en {lugar}"
        notificar("nuevo_reporte", texto, nuevo_id, mascota["id"])
    else:
        texto = f"{autor} reportó que encontró a {describir(mascota)} en {lugar}"
        notificar("encontrada", texto, nuevo_id, mascota["id"])
    return jsonify(mensaje="Reporte creado correctamente", id=nuevo_id), 201


# 2. GET /reportes  -> listar todos
@app.route("/reportes", methods=["GET"])
@token_requerido()
def listar_reportes():
    return jsonify(consultar(SQL_REPORTES + "ORDER BY r.id"))


# 3. GET /reportes/buscar  -> búsqueda con filtros (todos opcionales y combinables)
#    ?q=texto libre &ciudad= &lugar= &especie= &raza= &color= &tipo= &estado=
#    Todos los textos son LIBRES: no hace falta elegir de una lista; basta con escribir una parte.
def contiene(texto):
    return "%" + texto.strip() + "%"


@app.route("/reportes/buscar", methods=["GET"])
@token_requerido()
def buscar_reportes():
    a = request.args
    condiciones, valores = [], []
    if (a.get("q") or "").strip():
        # búsqueda general: nombre, especie, raza, color, señas particulares o lugar
        condiciones.append(
            "(m.nombre LIKE %s OR m.especie LIKE %s OR m.raza LIKE %s OR m.color LIKE %s "
            "OR m.descripcion LIKE %s OR r.lugar LIKE %s)"
        )
        valores.extend([contiene(a["q"])] * 6)
    if (a.get("ciudad") or "").strip():
        condiciones.append("r.lugar LIKE %s")        # el lugar se guarda como 'Ciudad - Barrio'
        valores.append(a["ciudad"].strip() + "%")
    if (a.get("lugar") or "").strip():
        condiciones.append("r.lugar LIKE %s")
        valores.append(contiene(a["lugar"]))
    if (a.get("especie") or "").strip():
        condiciones.append("m.especie LIKE %s")
        valores.append(contiene(a["especie"]))
    if (a.get("raza") or "").strip():
        condiciones.append("m.raza LIKE %s")
        valores.append(contiene(a["raza"]))
    if (a.get("color") or "").strip():
        condiciones.append("m.color LIKE %s")
        valores.append(contiene(a["color"]))
    if a.get("estado"):
        condiciones.append("r.estado = %s")
        valores.append(a["estado"])
    if a.get("tipo"):
        condiciones.append("r.tipo = %s")
        valores.append(a["tipo"])

    where = "WHERE " + " AND ".join(condiciones) + " " if condiciones else ""
    resultados = consultar(SQL_REPORTES + where + "ORDER BY r.fecha DESC, r.id DESC", tuple(valores))
    agregar_ultimo_avistamiento(resultados)
    return jsonify(total=len(resultados), resultados=resultados)


# 4. GET /reportes/filtros  -> sugerencias para los campos de filtro (igual se puede escribir cualquier cosa)
@app.route("/reportes/filtros", methods=["GET"])
@token_requerido()
def valores_filtros():
    filas = consultar(
        "SELECT r.lugar, m.especie, m.raza, m.color FROM reportes r JOIN mascotas m ON m.id = r.mascota_id"
    )
    ciudades = {f["lugar"].split(" - ")[0].strip() for f in filas}
    lugares = {f["lugar"].split(" - ", 1)[1].strip() for f in filas if " - " in f["lugar"]}
    return jsonify(
        ciudades=sorted(ciudades),
        lugares=sorted(lugares),
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
    agregar_ultimo_avistamiento([reporte])
    return jsonify(reporte)


# 7. PUT /reportes/<id>/estado  -> cambiar el estado (abierto / resuelto)
#    Es el botón "Ya apareció" de quien creó el reporte: ELLA confirma que la mascota sí fue encontrada.
@app.route("/reportes/<int:id>/estado", methods=["PUT"])
@token_requerido()
def cambiar_estado(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if not es_dueno_o_admin(reporte):
        return jsonify(error="Solo quien creó el reporte o un administrador puede cambiar su estado"), 403

    datos = request.get_json(silent=True) or {}
    if datos.get("estado") not in ("abierto", "resuelto"):
        return jsonify(error="El estado debe ser 'abierto' o 'resuelto'"), 400
    ejecutar("UPDATE reportes SET estado = %s WHERE id = %s", (datos["estado"], id))

    if datos["estado"] == "resuelto" and reporte["estado"] != "resuelto":
        mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
        registrar_novedad(reporte, "resuelto", estado="confirmada")
        if reporte["tipo"] == "perdida":
            notificar("encontrada", f"¡{titulo_mascota(mascota)} volvió a casa!", id, mascota["id"])
        else:
            notificar("encontrada", f"{titulo_mascota(mascota)} ya fue entregada a su familia", id, mascota["id"])
    return jsonify(mensaje="Estado del reporte actualizado", estado=datos["estado"])


# 8. PUT /reportes/<id>/encontrada  -> CUALQUIER usuario avisa que encontró la mascota (¡La encontré!)
#    El reporte NO se cierra solo: queda un aviso pendiente en el historial y le llega una notificación
#    a quien la busca. Ella confirma si de verdad es su mascota (ver /confirmar). A quien avisa se le
#    entrega el contacto de quien publicó el reporte para que pueda llamarle o escribirle de inmediato.
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
    if reporte["usuario_id"] == g.usuario["id"]:
        return jsonify(error="Este reporte es tuyo: usa «Ya apareció» para cerrarlo"), 400

    datos = request.get_json(silent=True) or {}
    falta = campos_faltantes(datos, ["lugar"])
    if falta:
        return jsonify(error="Indica dónde la encontraste", campos=falta), 400
    lugar = leer_texto(datos, "lugar", 120, "El lugar")
    descripcion = leer_texto(datos, "descripcion", 255, "Los detalles")
    condicion = leer_texto(datos, "condicion", 60, "El estado")

    previo = consultar(
        "SELECT id FROM novedades WHERE reporte_id = %s AND usuario_id = %s AND tipo = 'hallazgo' "
        "AND estado = 'abierta'", (id, g.usuario["id"]), uno=True)
    if previo:
        return jsonify(error="Ya avisaste que la encontraste. Quien la busca debe confirmarlo"), 409

    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    registrar_novedad(reporte, "hallazgo", lugar=lugar, descripcion=descripcion, condicion=condicion,
                      compartir_contacto=leer_si_no(datos, "compartir_contacto", True))
    texto = f"{primer_nombre()} dice que encontró a {titulo_mascota(mascota)} en {lugar}"
    if condicion:
        texto += f" ({condicion.lower()})"
    texto += ". Revisa el historial y confirma si es ella"
    notificar("encontrada", texto, id, mascota["id"], destinatario_id=reporte["usuario_id"])
    return jsonify(
        mensaje="¡Gracias! Le avisamos a quien la busca. Escríbele o llámale para coordinar la entrega",
        contacto=contacto_de(reporte["usuario_id"]),
    )


# 9. POST /reportes/<id>/avistamiento  -> "la vi por aquí" (sin cerrar el reporte)
#    Campos: lugar*, hace_minutos (cuándo la vio), condicion (cómo estaba), descripcion y
#    compartir_contacto (para que quien la busca pueda llamar a quien la vio).
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
    lugar = leer_texto(datos, "lugar", 120, "El lugar")
    descripcion = leer_texto(datos, "descripcion", 255, "Los detalles")
    condicion = leer_texto(datos, "condicion", 60, "El estado")
    try:
        hace_minutos = int(datos.get("hace_minutos") or 0)
    except (TypeError, ValueError):
        return jsonify(error="Indica hace cuánto la viste"), 400
    if not 0 <= hace_minutos <= 60 * 24 * 30:
        return jsonify(error="El momento en que la viste no es válido"), 400

    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    registrar_novedad(reporte, "avistamiento", lugar=lugar, descripcion=descripcion, condicion=condicion,
                      hace_minutos=hace_minutos, compartir_contacto=leer_si_no(datos, "compartir_contacto", False))

    texto = f"{primer_nombre()} vio a {titulo_mascota(mascota)} en {lugar} ({texto_hace(hace_minutos)})"
    if condicion:
        texto += f", {condicion.lower()}"
    if descripcion:
        texto += f": {descripcion}"
    notificar("avistamiento", texto, id, mascota["id"], destinatario_id=reporte["usuario_id"])
    return jsonify(
        mensaje="¡Gracias! Avisamos a quien la está buscando",
        contacto=contacto_de(reporte["usuario_id"]),
    ), 201


# 10. POST /reportes/<id>/reclamar  -> "creo que es mi mascota" (sobre un reporte de hallazgo)
#     A quien reclama se le entrega el contacto de quien la encontró.
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
    descripcion = leer_texto(datos, "descripcion", 255, "Los detalles")
    previo = consultar(
        "SELECT id FROM novedades WHERE reporte_id = %s AND usuario_id = %s AND tipo = 'reclamo' "
        "AND estado = 'abierta'", (id, g.usuario["id"]), uno=True)
    if previo:
        return jsonify(error="Ya avisaste que es tu mascota. Quien la encontró debe confirmarlo"), 409

    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)
    registrar_novedad(reporte, "reclamo", descripcion=descripcion,
                      compartir_contacto=leer_si_no(datos, "compartir_contacto", True))
    texto = f"{primer_nombre()} cree que {describir(mascota)} es su mascota y quiere contactarte"
    if descripcion:
        texto += f": {descripcion}"
    notificar("reclamo", texto, id, mascota["id"], destinatario_id=reporte["usuario_id"])
    return jsonify(
        mensaje="Le avisamos a quien la encontró. Escríbele o llámale para coordinar",
        contacto=contacto_de(reporte["usuario_id"]),
    ), 201


# 11. GET /reportes/<id>/contacto  -> cómo llamar o escribir a quien publicó el reporte
@app.route("/reportes/<int:id>/contacto", methods=["GET"])
@token_requerido()
def contacto_del_reporte(id):
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    if reporte["usuario_id"] == g.usuario["id"]:
        return jsonify(error="Este reporte es tuyo"), 400
    return jsonify(contacto=contacto_de(reporte["usuario_id"]))


# 12. GET /reportes/<id>/historial  -> todo lo que ha pasado con esa mascota (reportes y novedades)
#     Lo ven todos los usuarios con sesión. Los datos de contacto de quien dio un aviso solo los ve
#     quien publicó el reporte (o un administrador), y solo si esa persona decidió compartirlos.
@app.route("/reportes/<int:id>/historial", methods=["GET"])
@token_requerido()
def historial(id):
    reporte = consultar(SQL_REPORTES + "WHERE r.id = %s", (id,), uno=True)
    if not reporte:
        return jsonify(error="Reporte no encontrado"), 404
    agregar_ultimo_avistamiento([reporte])
    yo = g.usuario["id"]
    admin = g.usuario["rol"] == "admin"

    reportes = consultar(
        "SELECT r.id, r.tipo, r.estado, r.lugar, r.descripcion, r.fecha, r.usuario_id, u.nombre AS usuario "
        "FROM reportes r JOIN usuarios u ON u.id = r.usuario_id WHERE r.mascota_id = %s ORDER BY r.id",
        (reporte["mascota_id"],),
    )
    novedades = consultar(
        "SELECT n.id, n.reporte_id, n.usuario_id, n.tipo, n.estado, n.lugar, n.descripcion, n.condicion, "
        "n.hace_minutos, n.compartir_contacto, n.creado_en, u.nombre AS usuario, u.telefono, u.correo, "
        "rp.usuario_id AS dueno_id, rp.estado AS estado_reporte "
        "FROM novedades n JOIN usuarios u ON u.id = n.usuario_id JOIN reportes rp ON rp.id = n.reporte_id "
        "WHERE n.mascota_id = %s ORDER BY n.id",
        (reporte["mascota_id"],),
    )

    # Cuando alguien confirma un hallazgo se crea un reporte 'encontrada' a su nombre: ya sale como novedad
    confirmaron = {n["usuario_id"] for n in novedades if n["tipo"] == "hallazgo" and n["estado"] == "confirmada"}
    eventos = []
    for r in reportes:
        if r["tipo"] == "encontrada" and r["estado"] == "resuelto" and r["usuario_id"] in confirmaron:
            continue
        eventos.append({
            "clave": f"r{r['id']}", "clase": "reporte", "tipo": r["tipo"], "estado": r["estado"],
            "fecha": r["fecha"], "usuario": r["usuario"], "usuario_id": r["usuario_id"],
            "lugar": r["lugar"], "descripcion": r["descripcion"], "reporte_id": r["id"],
            "condicion": None, "visto_en": None, "puede_revisar": False, "contacto": None,
            "orden": (r["fecha"], 0, r["id"]),
        })
    for n in novedades:
        mio = admin or n["dueno_id"] == yo
        evento = {
            "clave": f"n{n['id']}", "clase": "novedad", "id": n["id"], "tipo": n["tipo"], "estado": n["estado"],
            "fecha": n["creado_en"], "visto_en": momento_visto(n["creado_en"], n["hace_minutos"]),
            "usuario": n["usuario"], "usuario_id": n["usuario_id"], "lugar": n["lugar"],
            "descripcion": n["descripcion"], "condicion": n["condicion"], "reporte_id": n["reporte_id"],
            "puede_revisar": bool(
                mio and n["tipo"] in ("hallazgo", "reclamo") and n["estado"] == "abierta"
                and n["estado_reporte"] == "abierto"
            ),
            "contacto": None,
            "orden": (n["creado_en"], 1, n["id"]),
        }
        if mio and n["compartir_contacto"] and n["usuario_id"] != yo and (n["telefono"] or n["correo"]):
            evento["contacto"] = {"nombre": n["usuario"], "telefono": n["telefono"] or None,
                                  "correo": n["correo"] or None}
        eventos.append(evento)

    eventos.sort(key=lambda e: e["orden"], reverse=True)
    for e in eventos:
        del e["orden"]
    return jsonify(reporte=reporte, es_dueno=es_dueno_o_admin(reporte), eventos=eventos)


# 13. PUT /reportes/<id>/novedades/<nid>/confirmar  -> quien publicó el reporte confirma un aviso
#     "Sí, es ella": el reporte se cierra como resuelto y se avisa a la comunidad y a quien ayudó.
@app.route("/reportes/<int:id>/novedades/<int:nid>/confirmar", methods=["PUT"])
@token_requerido()
def confirmar_novedad(id, nid):
    reporte, novedad, error = _cargar_novedad_revisable(id, nid)
    if error:
        return error
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)

    ejecutar("UPDATE novedades SET estado = 'confirmada' WHERE id = %s", (nid,))
    ejecutar("UPDATE reportes SET estado = 'resuelto' WHERE id = %s", (id,))
    if novedad["tipo"] == "hallazgo":
        # queda registrado el hallazgo a nombre de quien la encontró (suma a «fueron encontradas»)
        ejecutar(
            "INSERT INTO reportes (mascota_id, usuario_id, tipo, lugar, descripcion, estado) "
            "VALUES (%s, %s, 'encontrada', %s, %s, 'resuelto')",
            (reporte["mascota_id"], novedad["usuario_id"], novedad["lugar"] or reporte["lugar"], novedad["descripcion"]),
        )
    registrar_novedad(reporte, "resuelto", estado="confirmada")

    if reporte["tipo"] == "perdida":
        notificar("encontrada", f"¡{titulo_mascota(mascota)} volvió a casa!", id, mascota["id"])
    else:
        notificar("encontrada", f"{titulo_mascota(mascota)} ya fue entregada a su familia", id, mascota["id"])
    notificar("reclamo" if novedad["tipo"] == "reclamo" else "encontrada",
              f"{primer_nombre()} confirmó tu aviso sobre {titulo_mascota(mascota)}. ¡Gracias por ayudar!",
              id, mascota["id"], destinatario_id=novedad["usuario_id"])
    return jsonify(mensaje="¡Qué alegría! Dejamos el reporte como resuelto", estado="resuelto")


# 14. PUT /reportes/<id>/novedades/<nid>/descartar  -> "no era ella": el reporte sigue abierto
@app.route("/reportes/<int:id>/novedades/<int:nid>/descartar", methods=["PUT"])
@token_requerido()
def descartar_novedad(id, nid):
    reporte, novedad, error = _cargar_novedad_revisable(id, nid)
    if error:
        return error
    mascota = consultar("SELECT * FROM mascotas WHERE id = %s", (reporte["mascota_id"],), uno=True)

    ejecutar("UPDATE novedades SET estado = 'descartada' WHERE id = %s", (nid,))
    notificar("reclamo" if novedad["tipo"] == "reclamo" else "encontrada",
              f"Gracias por avisar. {primer_nombre()} indicó que no corresponde a {titulo_mascota(mascota)}",
              id, mascota["id"], destinatario_id=novedad["usuario_id"])
    return jsonify(mensaje="Listo, el reporte sigue abierto", estado=reporte["estado"])


def _cargar_novedad_revisable(id, nid):
    """Valida que el aviso exista, sea revisable y que quien pregunta pueda decidir sobre él."""
    reporte = consultar("SELECT * FROM reportes WHERE id = %s", (id,), uno=True)
    if not reporte:
        return None, None, (jsonify(error="Reporte no encontrado"), 404)
    if not es_dueno_o_admin(reporte):
        return None, None, (jsonify(error="Solo quien creó el reporte o un administrador puede revisar los avisos"), 403)
    novedad = consultar("SELECT * FROM novedades WHERE id = %s AND reporte_id = %s", (nid, id), uno=True)
    if not novedad:
        return None, None, (jsonify(error="Aviso no encontrado"), 404)
    if novedad["tipo"] not in ("hallazgo", "reclamo"):
        return None, None, (jsonify(error="Este tipo de aviso no necesita confirmación"), 400)
    if novedad["estado"] != "abierta" or reporte["estado"] != "abierto":
        return None, None, (jsonify(error="Este aviso ya fue revisado o el reporte ya está resuelto"), 409)
    return reporte, novedad, None


# ------------------------------------------------------------ notificaciones
def _ultima_leida():
    fila = consultar("SELECT ultima_id FROM lecturas_notificaciones WHERE usuario_id = %s",
                     (g.usuario["id"],), uno=True)
    return fila["ultima_id"] if fila else 0


# 15. GET /notificaciones  -> avisos de la comunidad + avisos privados para mí (lo más reciente primero)
@app.route("/notificaciones", methods=["GET"])
@token_requerido()
def listar_notificaciones():
    yo = g.usuario["id"]
    ultima = _ultima_leida()
    filas = consultar(
        "SELECT n.id, n.tipo, n.mensaje, n.reporte_id, n.mascota_id, n.creado_en, "
        "n.usuario_id AS autor_id, n.destinatario_id, m.nombre AS mascota, m.especie, m.color, m.foto_url, "
        "rp.usuario_id AS dueno_reporte "
        "FROM notificaciones n "
        "LEFT JOIN mascotas m ON m.id = n.mascota_id "
        "LEFT JOIN reportes rp ON rp.id = n.reporte_id "
        "WHERE (n.destinatario_id IS NULL OR n.destinatario_id = %s OR n.usuario_id = %s) "
        "ORDER BY n.id DESC LIMIT 50",
        (yo, yo),
    )
    for f in filas:
        propia = f["autor_id"] == yo
        f["leida"] = propia or f["id"] <= ultima
        if f["destinatario_id"] is not None:
            f["sobre_mi_reporte"] = (f["destinatario_id"] == yo) and not propia
        else:                                       # avisos antiguos o de toda la comunidad
            f["sobre_mi_reporte"] = (f["dueno_reporte"] == yo) and not propia
        f["es_mia"] = propia
        del f["dueno_reporte"]
        del f["destinatario_id"]
    return jsonify(no_leidas=sum(1 for f in filas if not f["leida"]), notificaciones=filas)


# 16. GET /notificaciones/resumen  -> solo el contador (lo consulta la campana de la barra)
@app.route("/notificaciones/resumen", methods=["GET"])
@token_requerido()
def resumen_notificaciones():
    yo = g.usuario["id"]
    n = consultar(
        "SELECT COUNT(*) AS n FROM notificaciones WHERE id > %s AND usuario_id <> %s "
        "AND (destinatario_id IS NULL OR destinatario_id = %s)",
        (_ultima_leida(), yo, yo), uno=True)["n"]
    return jsonify(no_leidas=n)


# 17. PUT /notificaciones/leer  -> marcar todo como leído
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
