from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from . import auth_bp
from forms import LoginForm
from models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el proceso de autenticación de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash,form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard.index'))
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form, title='Iniciar Sesión')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario actual"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('auth.login'))