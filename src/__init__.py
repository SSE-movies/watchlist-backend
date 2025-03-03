"""Watchlist API application package."""
from flask import Flask
from src.watchlist import watchlist_bp


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(watchlist_bp)

    return app
