# blueprints/ai_analysis/__init__.py
from flask import Blueprint

ai_analysis_bp = Blueprint('ai_analysis', __name__, template_folder='templates')

from blueprints.ai_analysis import routes