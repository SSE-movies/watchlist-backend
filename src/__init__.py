from flask import Flask
from src.watchlist import watchlist_bp


def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(watchlist_bp)
    
    return app
