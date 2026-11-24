import pymysql
from common import config


def conectar():
    """Abre una conexión nueva a MySQL."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=15,
        # Las fechas siempre salen en UTC; el frontend las convierte a la hora del celular
        init_command="SET time_zone = '+00:00'",
    )


def _texto_fechas(fila):
    """Convierte las fechas a texto (UTC) para poder devolverlas en JSON."""
    for clave, valor in fila.items():
        if hasattr(valor, "isoformat"):
            fila[clave] = valor.strftime("%Y-%m-%d %H:%M:%S")
    return fila


def consultar(sql, params=(), uno=False):
    """SELECT: devuelve una lista de filas (o una sola fila si uno=True)."""
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            if uno:
                fila = cur.fetchone()
                return _texto_fechas(fila) if fila else None
            return [_texto_fechas(f) for f in cur.fetchall()]
    finally:
        con.close()


def ejecutar(sql, params=()):
    """INSERT / UPDATE / DELETE: devuelve el id insertado (si aplica)."""
    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            return cur.lastrowid
    finally:
        con.close()
