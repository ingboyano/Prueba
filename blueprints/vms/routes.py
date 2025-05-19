from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

from . import vms_bp
from forms import VMForm
from models import VM, VMHistory
from extensions import db

@vms_bp.route('/list')
@login_required
def list_vms():
    """Lista todas las VMs con opción de filtrado por nombre"""
    if current_user.is_admin:
        # Los administradores ven todas las VMs
        vms = VM.query.all()
    else:
        # Los usuarios regulares solo ven sus propias VMs
        vms = VM.query.filter_by(created_by=current_user.id).all()
    
    return render_template('vms/list.html', vms=vms, title='Lista de VMs')

@vms_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_vm():
    """Formulario para crear una nueva solicitud de VM"""
    form = VMForm()
    
    if form.validate_on_submit():
        # Procesar el valor de vlans como lista
        vlans_list = []
        if form.vlans.data:
            vlans_list = [vlan.strip() for vlan in form.vlans.data.split(',') if vlan.strip()]
        
        # Crear la nueva VM
        vm = VM(
            name=form.name.data,
            requester_name=form.requester_name.data,
            requester_email=form.requester_email.data,
            primary_admin_name=form.primary_admin_name.data,
            primary_admin_email=form.primary_admin_email.data,
            secondary_admin_name=form.secondary_admin_name.data,
            secondary_admin_email=form.secondary_admin_email.data,
            cpu_count=form.cpu_count.data,
            ram_amount=form.ram_amount.data,
            disk_size=form.disk_size.data,
            operating_system=form.operating_system.data,
            physical_location=form.physical_location.data,
            virtual_host=form.virtual_host.data,
            backup_required=form.backup_required.data,
            backup_frequency=form.backup_frequency.data if form.backup_required.data else None,
            vlans=vlans_list,
            notes=form.notes.data,
            status='EN PEDIDO',
            created_by=current_user.id
        )
        
        db.session.add(vm)
        db.session.commit()
        
        flash('Solicitud de VM enviada exitosamente', 'success')
        return redirect(url_for('vms.list_vms'))
    
    return render_template('vms/form.html', form=form, title='Nueva Solicitud de VM')

@vms_bp.route('/<int:vm_id>')
@login_required
def view_vm(vm_id):
    """Muestra los detalles de una VM específica"""
    vm = VM.query.get_or_404(vm_id)
    
    # Verificar permisos: solo el creador o un administrador puede ver los detalles
    if not current_user.is_admin and current_user.id != vm.created_by:
        flash('No tienes permiso para ver esta VM', 'error')
        return redirect(url_for('vms.list_vms'))
    
    return render_template('vms/detail.html', vm=vm, title=f'VM: {vm.name}')

@vms_bp.route('/<int:vm_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vm(vm_id):
    """Edita una VM existente, solo permitido a administradores o creador"""
    vm = VM.query.get_or_404(vm_id)
    
    # Verificar permisos: solo el creador o un administrador puede editar
    if not current_user.is_admin and current_user.id != vm.created_by:
        flash('No tienes permiso para editar esta VM', 'error')
        return redirect(url_for('vms.list_vms'))
    
    # Convertir la lista de VLANs a cadena para el formulario
    vlans_str = ""
    if vm.vlans:
        vlans_str = ", ".join(vm.vlans)
    
    form = VMForm(obj=vm)
    form.vlans.data = vlans_str
    
    if form.validate_on_submit():
        # Guardar el estado anterior para historial
        previous_state = json.dumps(vm.to_dict())
        
        # Procesar el valor de vlans como lista
        vlans_list = []
        if form.vlans.data:
            vlans_list = [vlan.strip() for vlan in form.vlans.data.split(',') if vlan.strip()]
        
        # Actualizar datos
        form.populate_obj(vm)
        vm.vlans = vlans_list
        vm.updated_at = datetime.utcnow()
        
        # Historial
        history = VMHistory(
            vm_id=vm.id,
            previous_state=previous_state,
            modified_by=current_user.id,
            change_description=f"Actualización realizada por {current_user.username}"
        )
        
        db.session.add(history)
        db.session.commit()
        
        flash('VM actualizada exitosamente', 'success')
        return redirect(url_for('vms.view_vm', vm_id=vm.id))
    
    return render_template('vms/form.html', form=form, vm=vm, title=f'Editar VM: {vm.name}')

@vms_bp.route('/<int:vm_id>/status', methods=['POST'])
@login_required
def update_status(vm_id):
    """Actualiza el estado de una VM (solo para administradores)"""
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    
    vm = VM.query.get_or_404(vm_id)
    data = request.json
    new_status = data.get('status')
    
    if new_status in ['ACTIVO', 'RECHAZADO', 'PENDIENTE', 'EN PEDIDO']:
        # Guardar el estado anterior
        previous_state = json.dumps(vm.to_dict())
        
        # Crear registro de historial
        history = VMHistory(
            vm_id=vm.id,
            previous_state=previous_state,
            modified_by=current_user.id,
            change_description=f"Cambio de estado a '{new_status}' por {current_user.username}"
        )
        
        vm.status = new_status
        vm.updated_at = datetime.utcnow()
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({'status': 'éxito'})
    
    return jsonify({'error': 'Estado inválido'}), 400

@vms_bp.route('/<int:vm_id>/history')
@login_required
def vm_history(vm_id):
    """Muestra el historial de cambios de una VM"""
    vm = VM.query.get_or_404(vm_id)
    
    # Verificar permisos: solo el creador o un administrador puede ver el historial
    if not current_user.is_admin and current_user.id != vm.created_by:
        flash('No tienes permiso para ver el historial de esta VM', 'error')
        return redirect(url_for('vms.list_vms'))
    
    history = VMHistory.query.filter_by(vm_id=vm_id).order_by(VMHistory.created_at.desc()).all()
    
    return render_template('vms/history.html', vm=vm, history=history, title=f'Historial de {vm.name}')