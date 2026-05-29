"""
Fábrica de la aplicación Flask para el Parser CFG.
"""

from flask import Flask
from flask_cors import CORS

from app.api.rutas import blueprint_api


def crear_app() -> Flask:
    """Crea y configura la instancia de la aplicación Flask."""
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(blueprint_api, url_prefix="/api")

    return app
