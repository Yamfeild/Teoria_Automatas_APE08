"""
Detector de Ambigüedad Gramatical para expresiones booleanas.

Esta gramática NO es inherentemente ambigua porque la precedencia de
operadores está codificada en su estructura jerárquica. Sin embargo,
se detectan señales de ambigüedad práctica: patrones que en una
gramática simple (sin niveles de precedencia) producirían múltiples
árboles de derivación para la misma cadena.

Reglas de detección:
─────────────────────────────────────────────────────────────────────
Regla A — Operadores mezclados sin paréntesis:
    Si '|' y '&' aparecen en el mismo nivel de profundidad de
    paréntesis sin agrupación explícita, una gramática ingenua
    (sin precedencia) generaría más de un árbol de derivación.

Regla B — Operador encadenado sin agrupación:
    Expresiones como "A | B | C" o "A & B & C" son ambiguas en
    gramáticas sin reglas de asociatividad definidas.
─────────────────────────────────────────────────────────────────────
"""

from dataclasses import dataclass, field
from typing import List

from app.gramatica.lexer import Token


@dataclass
class ReporteAmbiguedad:
    """Resultado del análisis de ambigüedad sobre una expresión."""

    es_ambigua: bool
    razones: List[str] = field(default_factory=list)

    def a_dict(self) -> dict:
        return {
            "es_ambigua": self.es_ambigua,
            "razones": self.razones,
        }


def analizar_ambiguedad(tokens: List[Token]) -> ReporteAmbiguedad:
    """
    Analiza una lista de tokens en busca de señales de ambigüedad.

    Args:
        tokens: lista de tokens producida por el lexer.

    Returns:
        ReporteAmbiguedad con el resultado del análisis.
    """
    razones: List[str] = []

    tiene_or  = any(t.tipo == "|" for t in tokens)
    tiene_and = any(t.tipo == "&" for t in tokens)

    # Regla A: mezcla de | y & en el mismo nivel sin paréntesis
    if tiene_or and tiene_and:
        if _operadores_mezclados_mismo_nivel(tokens):
            razones.append(
                "La expresión mezcla operadores '|' (OR) y '&' (AND) en el mismo "
                "nivel de anidamiento sin paréntesis explícitos. En una gramática "
                "sin reglas de precedencia esto generaría múltiples árboles de derivación."
            )

    # Regla B: operador OR encadenado sin agrupación
    if _operador_encadenado(tokens, "|"):
        razones.append(
            "La expresión contiene múltiples operadores '|' en secuencia (ej. A | B | C). "
            "En una gramática sin reglas de asociatividad esto sería ambiguo."
        )

    # Regla B: operador AND encadenado sin agrupación
    if _operador_encadenado(tokens, "&"):
        razones.append(
            "La expresión contiene múltiples operadores '&' en secuencia (ej. A & B & C). "
            "En una gramática sin reglas de asociatividad esto sería ambiguo."
        )

    return ReporteAmbiguedad(es_ambigua=bool(razones), razones=razones)


# ------------------------------------------------------------------
# Funciones auxiliares internas
# ------------------------------------------------------------------

def _operadores_mezclados_mismo_nivel(tokens: List[Token]) -> bool:
    """
    Retorna True si '|' y '&' aparecen en la misma profundidad
    de paréntesis sin estar agrupados por paréntesis explícitos.
    """
    profundidad = 0
    operadores_por_nivel: dict = {}  # profundidad → conjunto de operadores vistos

    for token in tokens:
        if token.tipo == "(":
            profundidad += 1
        elif token.tipo == ")":
            profundidad -= 1
        elif token.tipo in ("|", "&"):
            if profundidad not in operadores_por_nivel:
                operadores_por_nivel[profundidad] = set()
            operadores_por_nivel[profundidad].add(token.tipo)

    for operadores in operadores_por_nivel.values():
        if "|" in operadores and "&" in operadores:
            return True

    return False


def _operador_encadenado(tokens: List[Token], tipo_op: str) -> bool:
    """
    Retorna True si el operador aparece dos o más veces en el nivel
    de profundidad 0 (sin paréntesis que lo envuelvan).
    """
    profundidad = 0
    contador = 0

    for token in tokens:
        if token.tipo == "(":
            profundidad += 1
        elif token.tipo == ")":
            profundidad -= 1
        elif token.tipo == tipo_op and profundidad == 0:
            contador += 1

    return contador >= 2
