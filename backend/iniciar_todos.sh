cd "$(dirname "$0")"
python3 usuarios_service/app.py &
python3 mascotas_service/app.py &
python3 reportes_service/app.py &
echo "Servicios iniciados (puertos 5001, 5002 y 5003). Ctrl+C para detener."
wait
