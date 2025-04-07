from flask import Blueprint

data_breach_bp = Blueprint('data_breach', __name__, template_folder='templates')

from blueprints.data_breach import routes