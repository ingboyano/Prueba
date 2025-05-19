#!/usr/bin/env python3
import os
import psycopg2
from werkzeug.security import generate_password_hash

def init_db():
    """Inicializar la base de datos usando el archivo schema.sql y crear usuarios predeterminados"""
    
    # Configuración de conexión desde variables de entorno o valores predeterminados
    db_name = os.environ.get('PGDATABASE', 'flow_vms')
    db_user = os.environ.get('PGUSER', 'flow_admin')
    db_password = os.environ.get('PGPASSWORD', 'clavesegura123')  # Sin caracteres especiales
    db_host = os.environ.get('PGHOST', 'localhost')
    db_port = os.environ.get('PGPORT', '5432')
    
    connection_string = f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"
    
    # Conectarse a la base de datos
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    
    # Leer y ejecutar el archivo schema.sql
    with open('schema.sql', 'r') as f:
        schema = f.read()
        cur.execute(schema)
    
    # Crear usuarios con contraseñas seguras (sin caracteres especiales como 'ñ')
    admin_password = generate_password_hash('SvaTecnica1')
    client_password = generate_password_hash('Personal2')
    
    # Verificar si ya existen usuarios antes de insertarlos
    cur.execute('SELECT COUNT(*) FROM "user"')
    count = cur.fetchone()[0]
    
    if count == 0:
        # Insertar usuarios solo si no existen
        cur.execute(
            'INSERT INTO "user" (username, password_hash, is_admin) VALUES (%s, %s, %s)',
            ('admin', admin_password, True)
        )
        cur.execute(
            'INSERT INTO "user" (username, password_hash, is_admin) VALUES (%s, %s, %s)',
            ('cliente', client_password, False)
        )
        print("Usuarios predeterminados creados exitosamente.")
    else:
        print("Se encontraron usuarios existentes. No se crearon nuevos usuarios predeterminados.")
    
    # Confirmar cambios y cerrar conexión
    conn.commit()
    cur.close()
    conn.close()
    
    print("La base de datos ha sido inicializada exitosamente.")

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")