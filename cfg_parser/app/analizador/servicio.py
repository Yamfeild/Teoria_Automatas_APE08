"""
Capa de Servicio — CFG Parser.

Orquesta el lexer, el analizador sintáctico y el detector de ambigüedad
en operaciones de alto nivel que consumen las rutas de la API.

Las rutas no deben importar componentes internos directamente;
todo pasa por esta capa.
"""

from dataclasses import dataclass
from typing import Optional

from app.gramatica.lexer import tokenizar, ErrorLexico
from app.gramatica.definicion import DEFINICION_GRAMATICA
from app.analizador.parser import AnalizadorSintactico, ErrorSintactico
from app.analizador.ambiguedad import analizar_ambiguedad, ReporteAmbiguedad
from app.analizador.arbol import NodoDerivacion


@dataclass
class ResultadoValidacion:
    """Resultado de validar una expresión booleana."""

    es_valida: bool
    expresion: str
    error: Optional[str] = None
    posicion_error: Optional[int] = None


@dataclass
class ResultadoAnalisis:
    """Resultado combinado: validación + ambigüedad + árbol opcional."""

    es_valida: bool
    expresion: str
    error: Optional[str] = None
    posicion_error: Optional[int] = None
    ambiguedad: Optional[ReporteAmbiguedad] = None
    arbol_derivacion: Optional[NodoDerivacion] = None


# ------------------------------------------------------------------
# Funciones de servicio públicas
# ------------------------------------------------------------------

def validar_expresion(expresion: str) -> ResultadoValidacion:
    """
    Determina si una cadena es sintácticamente válida según la gramática CFG.

    Args:
        expresion: cadena de entrada del usuario, ej. "A | ~(B & C)"

    Returns:
        ResultadoValidacion indicando si es válida y, de no serlo,
        el mensaje de error y la posición donde ocurrió.
    """
    expresion = expresion.strip()

    # Fase 1: análisis léxico
    try:
        tokens = tokenizar(expresion)
    except ErrorLexico as exc:
        return ResultadoValidacion(
            es_valida=False,
            expresion=expresion,
            error=str(exc),
            posicion_error=exc.posicion,
        )

    if not tokens:
        return ResultadoValidacion(
            es_valida=False,
            expresion=expresion,
            error="La expresión está vacía.",
        )

    # Fase 2: análisis sintáctico
    try:
        analizador = AnalizadorSintactico(tokens)
        analizador.analizar()
    except ErrorSintactico as exc:
        return ResultadoValidacion(
            es_valida=False,
            expresion=expresion,
            error=str(exc),
            posicion_error=exc.posicion,
        )

    return ResultadoValidacion(es_valida=True, expresion=expresion)


def analizar_expresion(
    expresion: str, construir_arbol: bool = False
) -> ResultadoAnalisis:
    """
    Valida una expresión, detecta ambigüedad y opcionalmente construye
    el árbol de derivación por la izquierda.

    Args:
        expresion      : cadena de entrada del usuario.
        construir_arbol: si es True, incluye el árbol de derivación en el resultado.

    Returns:
        ResultadoAnalisis con todos los datos del análisis.
    """
    expresion = expresion.strip()

    # Fase 1: análisis léxico
    try:
        tokens = tokenizar(expresion)
    except ErrorLexico as exc:
        return ResultadoAnalisis(
            es_valida=False,
            expresion=expresion,
            error=str(exc),
            posicion_error=exc.posicion,
        )

    if not tokens:
        return ResultadoAnalisis(
            es_valida=False,
            expresion=expresion,
            error="La expresión está vacía.",
        )

    # Fase 2: detección de ambigüedad (independiente de la validez)
    reporte_ambiguedad = analizar_ambiguedad(tokens)

    # Fase 3: análisis sintáctico
    arbol: Optional[NodoDerivacion] = None
    try:
        analizador = AnalizadorSintactico(tokens)
        arbol = analizador.analizar()
    except ErrorSintactico as exc:
        return ResultadoAnalisis(
            es_valida=False,
            expresion=expresion,
            error=str(exc),
            posicion_error=exc.posicion,
            ambiguedad=reporte_ambiguedad,
        )

    return ResultadoAnalisis(
        es_valida=True,
        expresion=expresion,
        ambiguedad=reporte_ambiguedad,
        arbol_derivacion=arbol if construir_arbol else None,
    )


def obtener_definicion_gramatica() -> dict:
    """Retorna la definición formal de la gramática como diccionario."""
    
    # Creamos un nuevo diccionario de producciones adaptado para el Frontend
    producciones_texto = {}
    for no_terminal, reglas in DEFINICION_GRAMATICA["producciones"].items():
        # Une cada lista de tokens en un solo texto. 
        # Ej: ["Exp", "|", "Term"] se convierte en "Exp | Term"
        producciones_texto[no_terminal] = [" ".join(regla) for regla in reglas]

    # Retornamos la estructura exacta que espera leer el JavaScript
    return {
        "no_terminales": DEFINICION_GRAMATICA["no_terminales"],
        "terminales": DEFINICION_GRAMATICA["terminales"],
        "simbolo_inicial": DEFINICION_GRAMATICA["simbolo_inicial"],
        "producciones": producciones_texto
    }
