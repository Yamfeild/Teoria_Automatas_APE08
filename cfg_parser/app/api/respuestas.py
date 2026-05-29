"""
Helpers para construir respuestas JSON consistentes en toda la API.

Todas las respuestas siguen el mismo sobre (envelope):

    {
        "exito":  true | false,
        "datos":  { ... } | null,
        "error":  null    | "mensaje de error"
    }
"""

from flask import jsonify
from typing import Any


def respuesta_exito(datos: Any, codigo: int = 200):
    """Construye una respuesta JSON exitosa."""
    return jsonify({"exito": True, "datos": datos, "error": None}), codigo


def respuesta_error(mensaje: str, codigo: int = 400):
    """Construye una respuesta JSON de error."""
    return jsonify({"exito": False, "datos": None, "error": mensaje}), codigo
