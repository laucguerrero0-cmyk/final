import os

# Configuración por variables de entorno para despliegue.
# En local puedes definirlas en el entorno antes de iniciar los servicios.
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "mascotas_rest_db")

# Define una clave segura en el entorno; no guardes secretos en GitHub.
SECRET_KEY = os.environ.get("SECRET_KEY", "")
HORAS_TOKEN = 2
