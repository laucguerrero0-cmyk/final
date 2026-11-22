import pymysql
import os
from common import config

conn = pymysql.connect(
    host="localhost",
    user="root",
    password=config.DB_PASSWORD,
    database="mascotas_rest_db",
    charset="utf8mb4"
)

cur = conn.cursor()
ruta_salida = "base_de_datos/mascotas_rest_db_FINAL.sql"
os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

print("Conectando a mascotas_rest_db...")
with open(ruta_salida, "w", encoding="utf-8") as f:
    f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
    cur.execute("SHOW TABLES")
    tablas = [row[0] for row in cur.fetchall()]
    print(f"Tablas encontradas: {tablas}")
    for tabla in tablas:
        print(f"Exportando {tabla}...")
        f.write(f"DROP TABLE IF EXISTS `{tabla}`;\n")
        cur.execute(f"SHOW CREATE TABLE `{tabla}`")
        create = cur.fetchone()[1]
        f.write(f"{create};\n\n")
        cur.execute(f"SELECT * FROM `{tabla}`")
        filas = cur.fetchall()
        columnas = [d[0] for d in cur.description]
        for fila in filas:
            vals = []
            for v in fila:
                if v is None: vals.append("NULL")
                elif isinstance(v, (int, float)): vals.append(str(v))
                else: vals.append("'" + str(v).replace("'", "''") + "'")
            cols = "`, `".join(columnas)
            f.write(f"INSERT INTO `{tabla}` (`{cols}`) VALUES ({', '.join(vals)});\n")
        f.write("\n")
    f.write("SET FOREIGN_KEY_CHECKS=1;\n")

print(f"¡LISTO! Archivo creado en {ruta_salida}")
cur.close()
conn.close()