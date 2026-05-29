"""
Punto de entrada de la aplicación CFG Parser.
Ejecutar este archivo para iniciar el servidor de desarrollo Flask.
"""

from app import crear_app

app = crear_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
