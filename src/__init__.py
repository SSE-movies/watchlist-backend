from flask import Flask
from config import Config
from .routes import watchlist_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(watchlist_bp)

    return app
