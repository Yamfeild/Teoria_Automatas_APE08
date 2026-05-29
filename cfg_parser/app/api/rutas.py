"""
Rutas de la API — CFG Boolean Expression Parser.

Prefijo base: /api  (registrado en app/__init__.py)

Endpoints
─────────────────────────────────────────────────────────────────────
GET  /api/salud
    Verificación de estado del servidor.

GET  /api/gramatica
    Retorna la definición formal de la gramática G = (V, Σ, P, S).

POST /api/validar
    Valida si una cadena pertenece al lenguaje de la gramática.
    Body: { "expresion": "A | ~B" }

POST /api/analizar
    Validación completa + detección de ambigüedad.
    Body: { "expresion": "A | B & C" }

POST /api/derivar
    Validación + ambigüedad + construcción del árbol de derivación.
    Body: { "expresion": "A | ~(B & C)" }
─────────────────────────────────────────────────────────────────────
"""

from flask import Blueprint, request

from app.api.respuestas import respuesta_exito, respuesta_error
from app.analizador.servicio import (
    validar_expresion,
    analizar_expresion,
    obtener_definicion_gramatica,
)

blueprint_api = Blueprint("api", __name__)


# ------------------------------------------------------------------
# GET /api/salud
# ------------------------------------------------------------------

@blueprint_api.get("/salud")
def verificar_salud():
    """
    Endpoint de verificación de estado (health check).

    Retorna:
        200 — { estado: "activo", mensaje: "..." }
    """
    return respuesta_exito({
        "estado": "activo",
        "mensaje": "CFG Parser API en funcionamiento.",
    })


# ------------------------------------------------------------------
# GET /api/gramatica
# ------------------------------------------------------------------

@blueprint_api.get("/gramatica")
def obtener_gramatica():
    """
    Retorna la definición formal de la gramática CFG.

    Retorna:
        200 — { no_terminales, terminales, simbolo_inicial, producciones }
    """
    return respuesta_exito(obtener_definicion_gramatica())


# ------------------------------------------------------------------
# POST /api/validar
# ------------------------------------------------------------------

@blueprint_api.post("/validar")
def validar():
    """
    Valida si una expresión booleana es sintácticamente correcta.

    Cuerpo de la solicitud (JSON):
        {
            "expresion": "A | ~(B & C)"
        }

    Respuesta exitosa (JSON):
        {
            "exito": true,
            "datos": {
                "expresion":      "A | ~(B & C)",
                "es_valida":      true,
                "error":          null,
                "posicion_error": null
            },
            "error": null
        }

    Respuesta con cadena inválida:
        {
            "exito": true,
            "datos": {
                "expresion":      "A | | B",
                "es_valida":      false,
                "error":          "Token inesperado '|' en la posición 4.",
                "posicion_error": 4
            },
            "error": null
        }
    """
    cuerpo = request.get_json(silent=True)

    if not cuerpo:
        return respuesta_error("El cuerpo de la solicitud debe ser JSON válido.")

    expresion = cuerpo.get("expresion")
    if expresion is None:
        return respuesta_error("El campo 'expresion' es requerido.")

    if not isinstance(expresion, str):
        return respuesta_error("El campo 'expresion' debe ser una cadena de texto.")

    resultado = validar_expresion(expresion)

    return respuesta_exito({
        "expresion":      resultado.expresion,
        "es_valida":      resultado.es_valida,
        "error":          resultado.error,
        "posicion_error": resultado.posicion_error,
    })


# ------------------------------------------------------------------
# POST /api/analizar
# ------------------------------------------------------------------

@blueprint_api.post("/analizar")
def analizar():
    """
    Valida una expresión y detecta señales de ambigüedad gramatical.

    Cuerpo de la solicitud (JSON):
        {
            "expresion": "A | B & C"
        }

    Respuesta (JSON):
        {
            "exito": true,
            "datos": {
                "expresion":      "A | B & C",
                "es_valida":      true,
                "error":          null,
                "posicion_error": null,
                "ambiguedad": {
                    "es_ambigua": true,
                    "razones": ["..."]
                }
            },
            "error": null
        }
    """
    cuerpo = request.get_json(silent=True)

    if not cuerpo:
        return respuesta_error("El cuerpo de la solicitud debe ser JSON válido.")

    expresion = cuerpo.get("expresion")
    if expresion is None:
        return respuesta_error("El campo 'expresion' es requerido.")

    if not isinstance(expresion, str):
        return respuesta_error("El campo 'expresion' debe ser una cadena de texto.")

    resultado = analizar_expresion(expresion, construir_arbol=False)

    return respuesta_exito({
        "expresion":      resultado.expresion,
        "es_valida":      resultado.es_valida,
        "error":          resultado.error,
        "posicion_error": resultado.posicion_error,
        "ambiguedad":     resultado.ambiguedad.a_dict() if resultado.ambiguedad else None,
    })


# ------------------------------------------------------------------
# POST /api/derivar
# ------------------------------------------------------------------

@blueprint_api.post("/derivar")
def derivar():
    """
    Valida, detecta ambigüedad y construye el árbol de derivación
    por la izquierda (leftmost derivation).

    Cuerpo de la solicitud (JSON):
        {
            "expresion": "A | ~(B & C)"
        }

    Respuesta (JSON):
        {
            "exito": true,
            "datos": {
                "expresion":      "A | ~(B & C)",
                "es_valida":      true,
                "error":          null,
                "posicion_error": null,
                "ambiguedad": {
                    "es_ambigua": false,
                    "razones":    []
                },
                "arbol_derivacion": {
                    "simbolo": "Exp",
                    "hijos": [ ... ]
                }
            },
            "error": null
        }
    """
    cuerpo = request.get_json(silent=True)

    if not cuerpo:
        return respuesta_error("El cuerpo de la solicitud debe ser JSON válido.")

    expresion = cuerpo.get("expresion")
    if expresion is None:
        return respuesta_error("El campo 'expresion' es requerido.")

    if not isinstance(expresion, str):
        return respuesta_error("El campo 'expresion' debe ser una cadena de texto.")

    resultado = analizar_expresion(expresion, construir_arbol=True)

    return respuesta_exito({
        "expresion":        resultado.expresion,
        "es_valida":        resultado.es_valida,
        "error":            resultado.error,
        "posicion_error":   resultado.posicion_error,
        "ambiguedad":       resultado.ambiguedad.a_dict() if resultado.ambiguedad else None,
        "arbol_derivacion": resultado.arbol_derivacion.a_dict() if resultado.arbol_derivacion else None,
    })
