#!/usr/bin/env python3
import os
import psycopg2

def migrate_database():
    """
    Script para actualizar la estructura de la base de datos cuando se añaden nuevos campos
    a los modelos. Ejecuta operaciones ALTER TABLE para añadir columnas sin perder datos.
    """
    
    # Configuración de conexión desde variables de entorno o valores predeterminados
    db_name = os.environ.get('PGDATABASE', 'flow_vms')
    db_user = os.environ.get('PGUSER', 'flow_admin')
    db_password = os.environ.get('PGPASSWORD', 'clavesegura123')
    db_host = os.environ.get('PGHOST', 'localhost')
    db_port = os.environ.get('PGPORT', '5432')
    
    connection_string = f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"
    
    try:
        # Conectarse a la base de datos
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
        
        print("Iniciando migración de la base de datos...")
        
        # Verificar si las tablas existen
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')")
        user_table_exists = cur.fetchone()[0]
        
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vm')")
        vm_table_exists = cur.fetchone()[0]
        
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vm_history')")
        vm_history_table_exists = cur.fetchone()[0]
        
        # Si no existen tablas, crear el esquema desde cero
        if not user_table_exists or not vm_table_exists or not vm_history_table_exists:
            print("No se encontraron tablas. Creando esquema desde cero...")
            with open('schema.sql', 'r') as f:
                schema_sql = f.read()
                cur.execute(schema_sql)
            print("Esquema creado correctamente.")
        else:
            print("Tablas existentes encontradas. Actualizando esquema...")
            
            # Migrar tabla de usuarios
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user' AND column_name = 'email')")
            if not cur.fetchone()[0]:
                print("Añadiendo columna 'email' a la tabla 'user'...")
                cur.execute("ALTER TABLE \"user\" ADD COLUMN email VARCHAR(120)")
            
            # Migrar tabla de VMs
            # Lista de columnas a verificar y añadir si no existen
            vm_columns = [
                ("requester_email", "VARCHAR(120)"),
                ("primary_admin_name", "VARCHAR(100)"),
                ("primary_admin_email", "VARCHAR(120)"),
                ("secondary_admin_name", "VARCHAR(100)"),
                ("secondary_admin_email", "VARCHAR(120)"),
                ("operating_system", "VARCHAR(100)"),
                ("virtual_host", "VARCHAR(200)"),
                ("backup_required", "BOOLEAN DEFAULT FALSE"),
                ("backup_frequency", "VARCHAR(50)"),
                ("vlans", "VARCHAR(100)[]")
            ]
            
            for column_name, column_type in vm_columns:
                cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'vm' AND column_name = '{column_name}')")
                if not cur.fetchone()[0]:
                    print(f"Añadiendo columna '{column_name}' a la tabla 'vm'...")
                    cur.execute(f"ALTER TABLE vm ADD COLUMN {column_name} {column_type}")
            
            # Si existe la columna infrastructure_location pero no virtual_host, renombrarla
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'vm' AND column_name = 'infrastructure_location')")
            infra_exists = cur.fetchone()[0]
            
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'vm' AND column_name = 'virtual_host')")
            vhost_exists = cur.fetchone()[0]
            
            if infra_exists and not vhost_exists:
                print("Renombrando columna 'infrastructure_location' a 'virtual_host'...")
                cur.execute("ALTER TABLE vm RENAME COLUMN infrastructure_location TO virtual_host")
            
            # Migrar tabla de historial
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'vm_history' AND column_name = 'change_description')")
            if not cur.fetchone()[0]:
                print("Añadiendo columna 'change_description' a la tabla 'vm_history'...")
                cur.execute("ALTER TABLE vm_history ADD COLUMN change_description VARCHAR(200)")
            
            # Crear índices si no existen
            indexes = [
                ("idx_vm_name", "CREATE INDEX idx_vm_name ON vm(name)"),
                ("idx_vm_status", "CREATE INDEX idx_vm_status ON vm(status)"),
                ("idx_vm_created_by", "CREATE INDEX idx_vm_created_by ON vm(created_by)"),
                ("idx_vm_history_vm_id", "CREATE INDEX idx_vm_history_vm_id ON vm_history(vm_id)"),
                ("idx_vm_history_modified_by", "CREATE INDEX idx_vm_history_modified_by ON vm_history(modified_by)")
            ]
            
            for index_name, create_index_sql in indexes:
                cur.execute(f"SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = '{index_name}')")
                if not cur.fetchone()[0]:
                    print(f"Creando índice '{index_name}'...")
                    cur.execute(create_index_sql)
        
        # Confirmar todos los cambios
        conn.commit()
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_database()