@echo off
REM Abre los 3 microservicios, cada uno en su propia ventana.
REM Ejecutar con doble clic estando dentro de la carpeta del proyecto.
cd /d "%~dp0"
start "Usuarios - puerto 5003" cmd /k python usuarios_service\app.py
start "Mascotas - puerto 5001" cmd /k python mascotas_service\app.py
start "Reportes - puerto 5002" cmd /k python reportes_service\app.py
echo Servicios iniciados. No cierre las 3 ventanas nuevas.
