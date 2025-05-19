from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from . import dashboard_bp
from models import VM
from extensions import db

@dashboard_bp.route('/')
@login_required
def index():
    """Muestra el panel de control principal con resumen de VMs y acciones rápidas"""
    # Obtener estadísticas
    vm_stats = {
        'total': VM.query.count(),
        'active': VM.query.filter_by(status='ACTIVO').count(),
        'pending': VM.query.filter_by(status='PENDIENTE').count(),
        'rejected': VM.query.filter_by(status='RECHAZADO').count(),
    }
    
    # Obtener VMs recientes (últimas 5)
    if current_user.is_admin:
        # Administradores ven todas las VMs
        recent_vms = VM.query.order_by(VM.request_date.desc()).limit(5).all()
    else:
        # Usuarios regulares sólo ven sus propias VMs
        recent_vms = VM.query.filter_by(created_by=current_user.id).order_by(VM.request_date.desc()).limit(5).all()
    
    return render_template('dashboard/index.html', 
                           vm_stats=vm_stats, 
                           recent_vms=recent_vms, 
                           title='Panel de Control')