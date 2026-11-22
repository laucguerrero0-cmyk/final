"""
Prueba automática de los 3 microservicios (equivale a lo que se hace a mano en Postman).
Con los 3 servicios encendidos:   python probar_endpoints.py
"""
import json
import requests

U = "http://localhost:5003"   # usuarios
M = "http://localhost:5001"   # mascotas
R = "http://localhost:5002"   # reportes

resultados = []


def probar(nombre, metodo, url, esperado, token=None, cuerpo=None):
    cabeceras = {"Authorization": "Bearer " + token} if token else {}
    r = requests.request(metodo, url, headers=cabeceras, json=cuerpo)
    ok = r.status_code == esperado
    print(("OK  " if ok else "FALLO"), metodo.ljust(6), url.replace("http://localhost", "").ljust(34),
          r.status_code, "(esperado", str(esperado) + ")")
    resultados.append({"nombre": nombre, "metodo": metodo, "ruta": url.split("localhost:")[1][4:],
                       "esperado": esperado, "obtenido": r.status_code, "ok": ok})
    try:
        return r.json()
    except ValueError:
        return {}


# ---------------- Usuarios y autenticación ----------------
tk_admin = probar("Login admin", "POST", U + "/auth/login", 200, cuerpo={"usuario": "admin", "password": "admin123"})["token"]
tk_laura = probar("Login laura", "POST", U + "/auth/login", 200, cuerpo={"usuario": "laura", "password": "laura123"})["token"]
tk_juan = probar("Login juan", "POST", U + "/auth/login", 200, cuerpo={"usuario": "juan", "password": "juan123"})["token"]
probar("Login con clave incorrecta", "POST", U + "/auth/login", 401, cuerpo={"usuario": "admin", "password": "mala"})
nuevo = probar("Registrar usuario", "POST", U + "/auth/registro", 201,
               cuerpo={"nombre": "Prueba Demo", "usuario": "demo_test", "password": "demo123", "correo": "demo@mascotas.com"})
probar("Registrar usuario repetido", "POST", U + "/auth/registro", 409,
       cuerpo={"nombre": "Prueba Demo", "usuario": "demo_test", "password": "demo123"})
probar("Registro sin campos", "POST", U + "/auth/registro", 400, cuerpo={"nombre": "Solo nombre"})
probar("Listar usuarios (admin)", "GET", U + "/usuarios", 200, token=tk_admin)
probar("Listar usuarios sin token", "GET", U + "/usuarios", 401)
probar("Listar usuarios siendo usuario normal", "GET", U + "/usuarios", 403, token=tk_laura)
probar("Consultar usuario propio", "GET", U + "/usuarios/2", 200, token=tk_laura)
probar("Consultar usuario ajeno", "GET", U + "/usuarios/3", 403, token=tk_laura)
probar("Consultar usuario inexistente", "GET", U + "/usuarios/999", 404, token=tk_admin)
probar("Actualizar usuario propio", "PUT", U + "/usuarios/2", 200, token=tk_laura, cuerpo={"correo": "laura.nueva@mascotas.com"})
probar("Token inválido", "GET", U + "/usuarios/2", 401, token="token.falso.123")

# ---------------- Mascotas ----------------
nueva = probar("Registrar mascota", "POST", M + "/mascotas", 201, token=tk_laura,
               cuerpo={"nombre": "Canela", "especie": "Perro", "raza": "Beagle", "color": "Café", "descripcion": "Orejas largas"})
id_m = nueva["id"]
probar("Registrar mascota incompleta", "POST", M + "/mascotas", 400, token=tk_laura, cuerpo={"raza": "Beagle"})
probar("Registrar mascota sin token", "POST", M + "/mascotas", 401, cuerpo={"nombre": "X", "especie": "Y"})
probar("Listar mascotas", "GET", M + "/mascotas", 200, token=tk_laura)
probar("Listar mascotas por especie", "GET", M + "/mascotas?especie=Gato", 200, token=tk_laura)
probar("Consultar mascota", "GET", M + "/mascotas/%d" % id_m, 200, token=tk_laura)
probar("Consultar mascota inexistente", "GET", M + "/mascotas/999", 404, token=tk_laura)
probar("Actualizar mascota (dueña)", "PUT", M + "/mascotas/%d" % id_m, 200, token=tk_laura, cuerpo={"color": "Café claro"})
probar("Actualizar mascota ajena", "PUT", M + "/mascotas/%d" % id_m, 403, token=tk_juan, cuerpo={"color": "Negro"})
probar("Eliminar mascota ajena", "DELETE", M + "/mascotas/%d" % id_m, 403, token=tk_juan)

# ---------------- Reportes ----------------
rep = probar("Crear reporte", "POST", R + "/reportes", 201, token=tk_laura,
             cuerpo={"mascota_id": id_m, "tipo": "perdida", "lugar": "Popayán - Parque Caldas", "descripcion": "Se perdió ayer"})
id_r = rep["id"]
probar("Crear reporte con tipo inválido", "POST", R + "/reportes", 400, token=tk_laura,
       cuerpo={"mascota_id": id_m, "tipo": "robada", "lugar": "X"})
probar("Crear reporte de mascota inexistente", "POST", R + "/reportes", 404, token=tk_laura,
       cuerpo={"mascota_id": 999, "tipo": "perdida", "lugar": "X"})
probar("Listar reportes", "GET", R + "/reportes", 200, token=tk_juan)
probar("Consultar reporte", "GET", R + "/reportes/%d" % id_r, 200, token=tk_juan)
probar("Consultar reporte inexistente", "GET", R + "/reportes/999", 404, token=tk_juan)
b = probar("Buscar por lugar", "GET", R + "/reportes/buscar?lugar=Popay", 200, token=tk_juan)
probar("Buscar por especie y estado", "GET", R + "/reportes/buscar?especie=Perro&estado=abierto", 200, token=tk_juan)
probar("Buscar por tipo", "GET", R + "/reportes/buscar?tipo=encontrada", 200, token=tk_juan)
probar("Cambiar estado de reporte ajeno", "PUT", R + "/reportes/%d/estado" % id_r, 403, token=tk_juan, cuerpo={"estado": "resuelto"})
probar("Cambiar estado con valor inválido", "PUT", R + "/reportes/%d/estado" % id_r, 400, token=tk_laura, cuerpo={"estado": "cerrado"})
probar("Cambiar estado (creadora)", "PUT", R + "/reportes/%d/estado" % id_r, 200, token=tk_laura, cuerpo={"estado": "resuelto"})
probar("Reportes sin token", "GET", R + "/reportes", 401)

# ---------------- Entrega final: filtros, avistamientos, notificaciones y planes ----------------
probar("Valores para los filtros", "GET", R + "/reportes/filtros", 200, token=tk_juan)
probar("Resumen del inicio", "GET", R + "/reportes/resumen", 200, token=tk_juan)
probar("Buscar por ciudad", "GET", R + "/reportes/buscar?ciudad=Popay%C3%A1n", 200, token=tk_juan)
probar("Buscar por raza y color", "GET", R + "/reportes/buscar?raza=Beagle&color=Caf%C3%A9", 200, token=tk_juan)
probar("Buscar por nombre", "GET", R + "/reportes/buscar?q=Canela", 200, token=tk_juan)

rep2 = probar("Crear otro reporte de pérdida", "POST", R + "/reportes", 201, token=tk_laura,
              cuerpo={"mascota_id": id_m, "tipo": "perdida", "lugar": "Popayán - Barrio Bolívar"})
id_r2 = rep2["id"]
probar("Avistamiento (otro usuario)", "POST", R + "/reportes/%d/avistamiento" % id_r2, 201, token=tk_juan,
       cuerpo={"lugar": "Popayán - Calle 5", "descripcion": "iba hacia el norte"})
probar("Avistamiento sin lugar", "POST", R + "/reportes/%d/avistamiento" % id_r2, 400, token=tk_juan, cuerpo={})
probar("Marcar encontrada sin lugar", "PUT", R + "/reportes/%d/encontrada" % id_r2, 400, token=tk_juan, cuerpo={})
probar("Marcar encontrada (cualquier usuario)", "PUT", R + "/reportes/%d/encontrada" % id_r2, 200, token=tk_juan,
       cuerpo={"lugar": "Popayán - Panadería La Esquina"})
probar("Marcar encontrada otra vez", "PUT", R + "/reportes/%d/encontrada" % id_r2, 409, token=tk_juan, cuerpo={"lugar": "X"})
probar("Avistamiento de reporte ya resuelto", "POST", R + "/reportes/%d/avistamiento" % id_r2, 400, token=tk_juan,
       cuerpo={"lugar": "X"})

hall = probar("Crear reporte de hallazgo", "POST", R + "/reportes", 201, token=tk_laura,
              cuerpo={"mascota_id": id_m, "tipo": "encontrada", "lugar": "Cali - Granada"})
probar("Reclamar mascota encontrada", "POST", R + "/reportes/%d/reclamar" % hall["id"], 201, token=tk_juan,
       cuerpo={"descripcion": "Es mi perra"})
probar("Reclamar un hallazgo propio", "POST", R + "/reportes/%d/reclamar" % hall["id"], 400, token=tk_laura, cuerpo={})

probar("Listar notificaciones", "GET", R + "/notificaciones", 200, token=tk_juan)
probar("Contador de notificaciones", "GET", R + "/notificaciones/resumen", 200, token=tk_juan)
probar("Marcar notificaciones como leídas", "PUT", R + "/notificaciones/leer", 200, token=tk_juan)
probar("Notificaciones sin token", "GET", R + "/notificaciones", 401)

foto = requests.post(M + "/mascotas/%d/foto" % id_m, headers={"Authorization": "Bearer " + tk_laura},
                     files={"foto": ("prueba.png", b"\x89PNG\r\n\x1a\n" + b"0" * 64, "image/png")})
resultados.append({"nombre": "Subir foto de mascota", "metodo": "POST", "ruta": "/mascotas/%d/foto" % id_m,
                   "esperado": 200, "obtenido": foto.status_code, "ok": foto.status_code == 200})
print(("OK  " if foto.status_code == 200 else "FALLO"), "POST  /mascotas/%d/foto" % id_m, foto.status_code)
probar("Subir foto de mascota ajena", "POST", M + "/mascotas/%d/foto" % id_m, 403, token=tk_juan)

planes = requests.get(U + "/planes").json()
probar("Listar planes (público)", "GET", U + "/planes", 200)
fund = next(p for p in planes if p["codigo"] == "fundacion")
hogar = next(p for p in planes if p["codigo"] == "hogar")
probar("Contratar fundación sin organización", "POST", U + "/suscripciones", 400, token=tk_laura,
       cuerpo={"plan_id": fund["id"], "periodo": "anual"})
probar("Contratar con periodo inválido", "POST", U + "/suscripciones", 400, token=tk_laura,
       cuerpo={"plan_id": hogar["id"], "periodo": "semanal"})
probar("Contratar plan Hogar", "POST", U + "/suscripciones", 201, token=tk_laura,
       cuerpo={"plan_id": hogar["id"], "periodo": "mensual"})
probar("Consultar mi plan", "GET", U + "/suscripciones/mia", 200, token=tk_laura)
probar("Contratar sin token", "POST", U + "/suscripciones", 401, cuerpo={"plan_id": hogar["id"], "periodo": "mensual"})
probar("Cancelar mi plan", "DELETE", U + "/suscripciones/mia", 200, token=tk_laura)

# ---------------- Limpieza de lo creado en la prueba ----------------
probar("Eliminar mascota (dueña)", "DELETE", M + "/mascotas/%d" % id_m, 200, token=tk_laura)
probar("Mascota ya eliminada", "GET", M + "/mascotas/%d" % id_m, 404, token=tk_laura)

total = len(resultados)
buenos = sum(r["ok"] for r in resultados)
print("\nRESULTADO: %d de %d pruebas correctas" % (buenos, total))
json.dump(resultados, open("resultados_pruebas.json", "w"), ensure_ascii=False, indent=1)
