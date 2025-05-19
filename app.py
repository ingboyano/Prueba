import os
from flask import Flask, render_template, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
import logging

# Importar extensiones desde extensions.py
from extensions import db, login_manager

def create_app(config_class=None):
    """
    Factory pattern para la creación de la aplicación Flask.
    Permite diferentes configuraciones (desarrollo, pruebas, producción)
    """
    app = Flask(__name__)
    
    # Configuración básica
    app.secret_key = "clave-segura-personalizada-desarrollo-1234567890"
    
    # Usar SQLite para pruebas en Replit
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///flow_vms.db'
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Configuración de logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Inicializar extensiones
    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar blueprints
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.vms import vms_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vms_bp)
    
    # Importar modelos
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carga un usuario desde la base de datos para Flask-Login"""
        return db.session.get(User, int(user_id))
    
    @app.route('/')
    def index():
        """Ruta principal - redirecciona al dashboard o login según estado de autenticación"""
        return redirect(url_for('dashboard.index'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Manejador para errores 404 - Página no encontrada"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Manejador para errores 500 - Error interno del servidor"""
        return render_template('errors/500.html'), 500
    
    # Crear tablas y usuarios por defecto
    with app.app_context():
        db.create_all()
        
        # Crear usuarios por defecto si no existen
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('SvaTecnica1'),
                is_admin=True,
                email='admin@example.com'  # Email por defecto
            )
            client = User(
                username='cliente',
                password_hash=generate_password_hash('Personal2'),
                is_admin=False,
                email='cliente@example.com'  # Email por defecto
            )
            db.session.add(admin)
            db.session.add(client)
            db.session.commit()
            app.logger.info('Usuarios predeterminados creados')
    
    return app

# Crear la instancia de la aplicación
app = create_app()