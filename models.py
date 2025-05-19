from flask_login import UserMixin
from datetime import datetime
import json
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=True)

    # Relaciones
    vms_created = db.relationship('VM', backref='creator', lazy=True)
    modifications = db.relationship('VMHistory', backref='modified_by_user', lazy=True, 
                                  foreign_keys='VMHistory.modified_by')

class VM(db.Model):
    """
    Modelo de Máquina Virtual que almacena todos los detalles de las solicitudes
    y configuraciones de VMs en el sistema.
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Información básica
    name = db.Column(db.String(100), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(120), nullable=True)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Administradores 
    primary_admin_name = db.Column(db.String(100), nullable=True)
    primary_admin_email = db.Column(db.String(120), nullable=True)
    secondary_admin_name = db.Column(db.String(100), nullable=True)
    secondary_admin_email = db.Column(db.String(120), nullable=True)
    
    # Especificaciones técnicas
    cpu_count = db.Column(db.Integer, nullable=False)
    ram_amount = db.Column(db.Integer, nullable=False)  # en GB
    disk_size = db.Column(db.Integer, nullable=False)   # en GB
    operating_system = db.Column(db.String(100), nullable=True)
    
    # Información de ubicación
    physical_location = db.Column(db.String(200), nullable=True)
    virtual_host = db.Column(db.String(200), nullable=True)
    
    # Configuración de respaldo
    backup_required = db.Column(db.Boolean, default=False)
    backup_frequency = db.Column(db.String(50), nullable=True)  # Diario, Semanal, Mensual, etc.
    
    # VLANs - Almacenadas como texto separado por comas en SQLite
    vlans_text = db.Column(db.Text, nullable=True)
    
    @property
    def vlans(self):
        """Obtiene la lista de VLANs desde el texto almacenado"""
        if self.vlans_text:
            return [vlan.strip() for vlan in self.vlans_text.split(',')]
        return []
    
    @vlans.setter
    def vlans(self, values):
        """Guarda la lista de VLANs como texto separado por comas"""
        if values:
            self.vlans_text = ', '.join(values)
        else:
            self.vlans_text = None
    
    # Notas y estado
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # PENDIENTE, APROBADO, RECHAZADO, ACTIVO
    
    # Metadatos
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    history = db.relationship('VMHistory', backref='vm', lazy=True, 
                             foreign_keys='VMHistory.vm_id')

    def to_dict(self):
        """Convierte el objeto VM a un diccionario para seguimiento de cambios y API"""
        return {
            'name': self.name,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'primary_admin_name': self.primary_admin_name,
            'primary_admin_email': self.primary_admin_email,
            'secondary_admin_name': self.secondary_admin_name,
            'secondary_admin_email': self.secondary_admin_email,
            'cpu_count': self.cpu_count,
            'ram_amount': self.ram_amount,
            'disk_size': self.disk_size,
            'operating_system': self.operating_system,
            'physical_location': self.physical_location,
            'virtual_host': self.virtual_host,
            'backup_required': self.backup_required,
            'backup_frequency': self.backup_frequency,
            'vlans': self.vlans,
            'notes': self.notes,
            'status': self.status
        }
        
    def __repr__(self):
        return f'<VM {self.name}>'

class VMHistory(db.Model):
    """
    Modelo para el seguimiento de cambios en las VMs,
    almacena el estado anterior para auditoria.
    """
    id = db.Column(db.Integer, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'), nullable=False)
    previous_state = db.Column(db.Text, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    change_description = db.Column(db.String(200), nullable=True)

    def previous_state_dict(self):
        """Convierte el estado anterior almacenado como JSON a un diccionario"""
        try:
            return json.loads(self.previous_state)
        except json.JSONDecodeError:
            return {'error': 'Estado anterior inválido'}