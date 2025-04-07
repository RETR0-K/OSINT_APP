# blueprints/home/__init__.py
from flask import Blueprint

home_bp = Blueprint('home', __name__, template_folder='templates', url_prefix='/')

from blueprints.home import routes