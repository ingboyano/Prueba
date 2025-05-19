-- Borrar tablas si existen (para resetear la BD) - Comentar estas líneas si no se desea borrar datos
DROP TABLE IF EXISTS vm_history;
DROP TABLE IF EXISTS vm;
DROP TABLE IF EXISTS "user";

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    email VARCHAR(120)
);

-- Tabla de máquinas virtuales
CREATE TABLE IF NOT EXISTS vm (
    id SERIAL PRIMARY KEY,
    -- Información básica
    name VARCHAR(100) NOT NULL,
    requester_name VARCHAR(100) NOT NULL,
    requester_email VARCHAR(120),
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Administradores
    primary_admin_name VARCHAR(100),
    primary_admin_email VARCHAR(120),
    secondary_admin_name VARCHAR(100),
    secondary_admin_email VARCHAR(120),
    
    -- Especificaciones técnicas
    cpu_count INTEGER NOT NULL,
    ram_amount INTEGER NOT NULL,
    disk_size INTEGER NOT NULL,
    operating_system VARCHAR(100),
    
    -- Información de ubicación
    physical_location VARCHAR(200),
    virtual_host VARCHAR(200),
    
    -- Configuración de respaldo
    backup_required BOOLEAN DEFAULT FALSE,
    backup_frequency VARCHAR(50),
    
    -- VLANs - Lista dinámica
    vlans VARCHAR(100)[],
    
    -- Notas y estado
    notes TEXT,
    status VARCHAR(20) NOT NULL,
    
    -- Metadatos
    created_by INTEGER NOT NULL REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de historial de máquinas virtuales
CREATE TABLE IF NOT EXISTS vm_history (
    id SERIAL PRIMARY KEY,
    vm_id INTEGER NOT NULL REFERENCES vm(id),
    previous_state TEXT NOT NULL,
    modified_by INTEGER NOT NULL REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_description VARCHAR(200)
);

-- No se incluyen usuarios por defecto aquí, se crearán a través de init_db.py
-- usando Werkzeug para generar correctamente los hashes de contraseña

-- Indexes para mejorar el rendimiento de búsquedas comunes
CREATE INDEX idx_vm_name ON vm(name);
CREATE INDEX idx_vm_status ON vm(status);
CREATE INDEX idx_vm_created_by ON vm(created_by);
CREATE INDEX idx_vm_history_vm_id ON vm_history(vm_id);
CREATE INDEX idx_vm_history_modified_by ON vm_history(modified_by);