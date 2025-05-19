from flask import Blueprint

vms_bp = Blueprint('vms', __name__, url_prefix='/vms')

from . import routes  # noqa