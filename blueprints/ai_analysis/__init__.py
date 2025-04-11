# blueprints/ai_analysis/__init__.py
from flask import Blueprint

# Create the blueprint instance
ai_analysis_bp = Blueprint('ai_analysis', __name__, template_folder='templates')

# Import routes at the end to avoid circular imports
from blueprints.ai_analysis import routes