from flask import Flask, render_template
from config import Config
from blueprints.home import home_bp
from blueprints.data_breach import data_breach_bp
from blueprints.username_search import username_search_bp
from blueprints.ai_analysis import ai_analysis_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(home_bp, url_prefix='/')
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
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)