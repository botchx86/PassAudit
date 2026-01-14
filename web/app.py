"""
Flask Application Factory
Main application initialization and configuration
"""

import os
import sys
from flask import Flask, session
from datetime import timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_app(config=None):
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

    # Apply custom config if provided
    if config:
        app.config.update(config)

    # Register blueprints
    from web.routes.main import main_bp
    from web.routes.analyze import analyze_bp
    from web.routes.generate import generate_bp
    from web.routes.api_routes import api_bp
    from web.routes.config_routes import config_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(config_bp, url_prefix='/config')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # CSP header - adjust as needed
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
        return response

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
