# -*- coding: utf-8 -*-
"""
Punto de entrada de la aplicacion CFG Parser.
Ejecutar este archivo para iniciar el servidor de desarrollo Flask.
"""
import os
from flask import Flask, render_template
from flask_cors import CORS

from app.api.rutas import blueprint_api

# 1. Definimos la ruta absoluta basada en dónde está este archivo (run.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def crear_app() -> Flask:
    # 2. Le pasamos las rutas absolutas directamente a la app principal
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
        static_url_path="/static"
    )
    CORS(app)

    # 3. Registramos solo la API
    app.register_blueprint(blueprint_api, url_prefix="/api")

    # 4. La ruta principal la maneja directamente la app
    @app.get("/")
    def index():
        return render_template("index.html")

    return app

app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)