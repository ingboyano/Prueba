# Guía de Instalación en Producción - Flow VMs

Esta guía proporciona instrucciones detalladas para la instalación del sistema de gestión de VMs en un servidor de producción con Ubuntu 24.04 LTS.

## Requisitos previos

- Servidor Ubuntu 24.04 LTS
- Python 3.8+
- PostgreSQL 16
- Apache 2.4 con mod_wsgi
- Permisos de sudo para instalar paquetes

## 1. Preparación del sistema

Actualiza el sistema e instala las dependencias necesarias:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev
sudo apt install -y postgresql postgresql-contrib apache2 libapache2-mod-wsgi-py3 git
```

## 2. Configuración de PostgreSQL

### Instalar PostgreSQL 16:

```bash
# Añadir el repositorio de PostgreSQL 16
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16
```

### Configurar la base de datos:

```bash
sudo -u postgres psql

# En la consola de PostgreSQL
CREATE USER flow_vms_user WITH PASSWORD 'contraseña_segura';
CREATE DATABASE flow_vms;
GRANT ALL PRIVILEGES ON DATABASE flow_vms TO flow_vms_user;
\q
```

### Cargar el esquema de la base de datos:

```bash
# Asumimos que schema.sql está en el mismo directorio que esta guía
sudo -u postgres psql -d flow_vms -f schema.sql

# O inicializar desde la aplicación
cd /var/www/html/org.vms
sudo -u www-data python3 init_db.py
```

## 3. Configuración de la aplicación

### Clonar el repositorio o copiar los archivos:

```bash
sudo mkdir -p /var/www/html/org.vms
sudo chown www-data:www-data /var/www/html/org.vms
cd /var/www/html/org.vms
# Asumiendo que los archivos se copian manualmente o se clonan desde git
```

### Configurar el entorno virtual:

```bash
cd /var/www/html/org.vms
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/pip install gunicorn psycopg2-binary
```

### Crear archivo de configuración .env para variables de entorno:

```bash
sudo -u www-data nano /var/www/html/org.vms/.env
```

Contenido del archivo .env:
```
SESSION_SECRET=clave_secreta_personalizada_muy_segura
DATABASE_URL=postgresql://flow_vms_user:contraseña_segura@localhost/flow_vms
```

## 4. Configuración de Apache y WSGI

### Crear el archivo de configuración de Apache:

```bash
sudo nano /etc/apache2/sites-available/flow-vms.conf
```

Contenido del archivo flow-vms.conf:
```apache
<VirtualHost *:80>
    ServerName vms.example.org
    ServerAdmin webmaster@example.org
    
    DocumentRoot /var/www/html/org.vms
    
    <Directory /var/www/html/org.vms>
        Require all granted
    </Directory>
    
    WSGIDaemonProcess flow_vms user=www-data group=www-data threads=5 python-home=/var/www/html/org.vms/venv
    WSGIScriptAlias / /var/www/html/org.vms/app.wsgi
    
    <Directory /var/www/html/org.vms>
        WSGIProcessGroup flow_vms
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/flow-vms-error.log
    CustomLog ${APACHE_LOG_DIR}/flow-vms-access.log combined
</VirtualHost>
```

### Crear archivo WSGI:

```bash
sudo -u www-data nano /var/www/html/org.vms/app.wsgi
```

Contenido del archivo app.wsgi:
```python
#!/usr/bin/python3
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Añadir directorio de la aplicación al path
sys.path.insert(0, BASE_DIR)

# Importar la aplicación
from app import app as application
```

### Activar el sitio y reiniciar Apache:

```bash
sudo a2ensite flow-vms.conf
sudo systemctl restart apache2
```

## 5. Configuración de SSL (opcional pero recomendado)

### Instalar Certbot y configurar HTTPS:

```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d vms.example.org
```

## 6. Mantenimiento

### Actualizar la aplicación:

```bash
cd /var/www/html/org.vms
sudo -u www-data git pull  # Si se usa git
sudo systemctl restart apache2
```

### Backup de la base de datos:

```bash
sudo -u postgres pg_dump flow_vms > /path/to/backup/flow_vms_$(date +%Y%m%d).sql
```

### Restaurar la base de datos:

```bash
sudo -u postgres psql flow_vms < /path/to/backup/flow_vms_YYYYMMDD.sql
```

## 7. Solución de problemas

### Verificar logs:

```bash
# Logs de Apache
sudo tail -f /var/log/apache2/flow-vms-error.log

# Logs de la aplicación (si se configuran)
sudo tail -f /var/www/html/org.vms/logs/app.log
```

### Verificar permisos:

```bash
sudo chown -R www-data:www-data /var/www/html/org.vms
sudo chmod -R 755 /var/www/html/org.vms
```

### Verificar conectividad a la base de datos:

```bash
cd /var/www/html/org.vms
sudo -u www-data ./venv/bin/python -c "import psycopg2; conn = psycopg2.connect('postgresql://flow_vms_user:contraseña_segura@localhost/flow_vms'); print('Conexión exitosa')"
```

---

Para cualquier consulta o problema, contactar al equipo de soporte técnico.