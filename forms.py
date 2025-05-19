from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, IntegerField, SubmitField, TextAreaField, 
                    EmailField, SelectField, BooleanField)
from wtforms.validators import DataRequired, NumberRange, Email, Optional, ValidationError

class LoginForm(FlaskForm):
    """
    Formulario para la autenticación de usuarios.
    """
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class VMForm(FlaskForm):
    """
    Formulario para la creación y edición de solicitudes de VM.
    Incluye todos los campos requeridos según las especificaciones.
    """
    # Información básica
    name = StringField('Nombre de VM', validators=[DataRequired()])
    requester_name = StringField('Nombre del Solicitante', validators=[DataRequired()])
    requester_email = EmailField('Correo del Solicitante', validators=[
        Optional(),
        Email(message='Por favor ingrese un correo válido')
    ])
    
    # Administradores
    primary_admin_name = StringField('Nombre del Administrador Principal', validators=[Optional()])
    primary_admin_email = EmailField('Correo del Administrador Principal', validators=[
        Optional(),
        Email(message='Por favor ingrese un correo válido')
    ])
    secondary_admin_name = StringField('Nombre del Administrador Secundario', validators=[Optional()])
    secondary_admin_email = EmailField('Correo del Administrador Secundario', validators=[
        Optional(),
        Email(message='Por favor ingrese un correo válido')
    ])
    
    # Especificaciones técnicas
    cpu_count = IntegerField('Número de CPUs', validators=[
        DataRequired(),
        NumberRange(min=1, message="Debe tener al menos 1 CPU")
    ])
    ram_amount = IntegerField('Cantidad de RAM (GB)', validators=[
        DataRequired(),
        NumberRange(min=1, message="Debe tener al menos 1 GB de RAM")
    ])
    disk_size = IntegerField('Tamaño de Disco (GB)', validators=[
        DataRequired(),
        NumberRange(min=10, message="Debe tener al menos 10 GB de disco")
    ])
    operating_system = SelectField('Sistema Operativo', choices=[
        ('', 'Seleccione un sistema operativo'),
        ('windows_server_2022', 'Windows Server 2022'),
        ('windows_server_2019', 'Windows Server 2019'),
        ('ubuntu_22_04', 'Ubuntu 22.04 LTS'),
        ('ubuntu_24_04', 'Ubuntu 24.04 LTS'),
        ('rhel_9', 'Red Hat Enterprise Linux 9'),
        ('centos_stream_9', 'CentOS Stream 9'),
        ('debian_12', 'Debian 12'),
        ('other', 'Otro (especificar en notas)')
    ], validators=[Optional()])
    
    # Información de ubicación
    physical_location = StringField('Ubicación Física', validators=[Optional()])
    virtual_host = StringField('Host Virtual / Infraestructura', validators=[Optional()])
    
    # Configuración de respaldo
    backup_required = BooleanField('Requiere Respaldo', default=False)
    backup_frequency = SelectField('Frecuencia de Respaldo', choices=[
        ('', 'No aplica'),
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('custom', 'Personalizada (especificar en notas)')
    ], validators=[Optional()])
    
    # VLANs
    vlans = StringField('VLANs (separadas por coma)', validators=[Optional()],
                       description="Ejemplo: vlan-prod-1,vlan-dev-2")
    
    # Notas
    notes = TextAreaField('Notas Adicionales', validators=[Optional()])
    
    submit = SubmitField('Enviar Solicitud')
    
    def validate_backup_frequency(self, field):
        """Valida que la frecuencia de respaldo esté configurada si se requiere respaldo"""
        if self.backup_required.data and not field.data:
            raise ValidationError('Por favor seleccione una frecuencia de respaldo')