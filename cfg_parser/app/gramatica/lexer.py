"""
Analizador Léxico (tokenizador) para expresiones booleanas.

Convierte una cadena de texto en una lista de Tokens que el
analizador sintáctico puede procesar.

Tokens soportados:
  id  — cualquier secuencia de letras/dígitos (ej. A, B, miVar)
  |   — operador OR
  &   — operador AND
  ~   — operador NOT
  (   — paréntesis izquierdo
  )   — paréntesis derecho
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    """Representa un único token léxico."""

    tipo: str      # ej. 'id', '|', '&', '~', '(', ')'
    valor: str     # texto original del token
    posicion: int  # índice (base 0) en la cadena original


class ErrorLexico(Exception):
    """Se lanza cuando el lexer encuentra un carácter no reconocido."""

    def __init__(self, caracter: str, posicion: int):
        super().__init__(
            f"Carácter inesperado '{caracter}' en la posición {posicion}."
        )
        self.caracter = caracter
        self.posicion = posicion


def tokenizar(expresion: str) -> List[Token]:
    """
    Convierte una expresión booleana en una lista de Tokens.

    Args:
        expresion: cadena de entrada, ej. "A | ~(B & C)"

    Returns:
        Lista ordenada de objetos Token.

    Raises:
        ErrorLexico: si se encuentra un carácter no reconocido.
    """
    tokens: List[Token] = []
    indice = 0

    while indice < len(expresion):
        caracter = expresion[indice]

        # Ignorar espacios en blanco
        if caracter.isspace():
            indice += 1
            continue

        # Identificadores (id): letras y dígitos
        if caracter.isalpha() or caracter.isdigit():
            inicio = indice
            while indice < len(expresion) and (
                expresion[indice].isalpha() or expresion[indice].isdigit()
            ):
                indice += 1
            tokens.append(
                Token(tipo="id", valor=expresion[inicio:indice], posicion=inicio)
            )
            continue

        # Operadores y paréntesis
        if caracter in ("|", "&", "~", "(", ")"):
            tokens.append(Token(tipo=caracter, valor=caracter, posicion=indice))
            indice += 1
            continue

        raise ErrorLexico(caracter=caracter, posicion=indice)

    return tokens
