# blueprints/username_search/__init__.py
from flask import Blueprint

username_search_bp = Blueprint('username_search', __name__, template_folder='templates')

from blueprints.username_search import routes