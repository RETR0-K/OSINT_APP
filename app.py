from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

# Import blueprints
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.data_breach import data_breach_bp
from blueprints.username_search import username_search_bp
from blueprints.ai_analysis import ai_analysis_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Enable Jinja2 'do' extension for template operations
    app.jinja_env.add_extension('jinja2.ext.do')
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(data_breach_bp, url_prefix='/data-breach')
    app.register_blueprint(username_search_bp, url_prefix='/username-search')
    app.register_blueprint(ai_analysis_bp, url_prefix='/ai-analysis')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error_code=404, error_message="Page not found"), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error_code=500, error_message="Internal server error"), 500
    
    # Set up jinja global functions and variables
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        return {
            'now': __import__('datetime').datetime.now(),
            'config': app.config,
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created or verified.")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')