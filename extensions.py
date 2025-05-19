"""
Este archivo contiene las extensiones de Flask que se utilizan en toda la aplicación.
Soluciona problemas de importación circular al proporcionar un punto central para instanciación.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Base declarativa para SQLAlchemy
class Base(DeclarativeBase):
    pass

# Instancias de extensiones
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()