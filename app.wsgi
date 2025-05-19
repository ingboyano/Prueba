#!/usr/bin/python3
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    filename='/var/log/flow-vms/app.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Configurar variables de entorno
# En producción, se recomienda usar un archivo .env
os.environ['SESSION_SECRET'] = 'clave_secreta_personalizada_muy_segura'
os.environ['DATABASE_URL'] = 'postgresql://flow_vms_user:contraseña_segura@localhost/flow_vms'

# Añadir directorio de la aplicación al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Importar la aplicación
from app import app as application