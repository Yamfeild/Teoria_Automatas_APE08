"""
Analizador Sintáctico Descendente Recursivo para la CFG booleana.

Implementa la gramática con precedencia de operadores codificada
estructuralmente en los niveles de los métodos de análisis:

    Exp    → Term (| Term)*          — OR,  menor precedencia
    Term   → Factor (& Factor)*      — AND, precedencia media
    Factor → ~ Factor | ( Exp ) | id — NOT, mayor precedencia

Cada símbolo no terminal de la gramática tiene su propio método:
    _analizar_exp()    → Exp
    _analizar_term()   → Term
    _analizar_factor() → Factor

El analizador produce una derivación por la izquierda (leftmost derivation).
"""

from typing import List, Optional

from app.gramatica.lexer import Token
from app.analizador.arbol import NodoDerivacion


class ErrorSintactico(Exception):
    """Se lanza cuando la cadena no es válida según la gramática."""

    def __init__(self, mensaje: str, posicion: Optional[int] = None):
        super().__init__(mensaje)
        self.posicion = posicion


class AnalizadorSintactico:
    """
    Analizador sintáctico descendente recursivo para expresiones booleanas.

    Uso:
        analizador = AnalizadorSintactico(tokens)
        arbol      = analizador.analizar()   # lanza ErrorSintactico si es inválida
    """

    def __init__(self, tokens: List[Token]):
        self._tokens = tokens
        self._pos = 0

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def analizar(self) -> NodoDerivacion:
        """
        Analiza el flujo de tokens completo y retorna la raíz del árbol.

        Returns:
            NodoDerivacion raíz del árbol de derivación.

        Raises:
            ErrorSintactico: si la expresión no es sintácticamente válida.
        """
        arbol = self._analizar_exp()

        if not self._fin_de_entrada():
            token = self._token_actual()
            raise ErrorSintactico(
                f"Token inesperado '{token.valor}' en la posición {token.posicion}.",
                posicion=token.posicion,
            )

        return arbol

    # ------------------------------------------------------------------
    # Regla: Exp → Term (| Term)*
    # ------------------------------------------------------------------

    def _analizar_exp(self) -> NodoDerivacion:
        nodo = NodoDerivacion(simbolo="Exp")
        izquierda = self._analizar_term()

        if self._coincide("|"):
            # Exp → Exp | Term  (asociatividad izquierda)
            self._consumir("|")
            derecha = self._analizar_term()

            exp_interno = NodoDerivacion(simbolo="Exp", hijos=[izquierda])
            nodo.hijos = [
                exp_interno,
                NodoDerivacion(simbolo="|"),
                derecha,
            ]

            # Encadenamiento: A | B | C → ((A | B) | C)
            while self._coincide("|"):
                self._consumir("|")
                siguiente_term = self._analizar_term()
                nuevo_exp = NodoDerivacion(
                    simbolo="Exp",
                    hijos=[
                        NodoDerivacion(simbolo="Exp", hijos=nodo.hijos),
                        NodoDerivacion(simbolo="|"),
                        siguiente_term,
                    ],
                )
                nodo = nuevo_exp
        else:
            # Exp → Term
            nodo.hijos = [izquierda]

        return nodo

    # ------------------------------------------------------------------
    # Regla: Term → Factor (& Factor)*
    # ------------------------------------------------------------------

    def _analizar_term(self) -> NodoDerivacion:
        nodo = NodoDerivacion(simbolo="Term")
        izquierda = self._analizar_factor()

        if self._coincide("&"):
            # Term → Term & Factor  (asociatividad izquierda)
            self._consumir("&")
            derecha = self._analizar_factor()

            term_interno = NodoDerivacion(simbolo="Term", hijos=[izquierda])
            nodo.hijos = [
                term_interno,
                NodoDerivacion(simbolo="&"),
                derecha,
            ]

            # Encadenamiento: A & B & C → ((A & B) & C)
            while self._coincide("&"):
                self._consumir("&")
                siguiente_factor = self._analizar_factor()
                nuevo_term = NodoDerivacion(
                    simbolo="Term",
                    hijos=[
                        NodoDerivacion(simbolo="Term", hijos=nodo.hijos),
                        NodoDerivacion(simbolo="&"),
                        siguiente_factor,
                    ],
                )
                nodo = nuevo_term
        else:
            # Term → Factor
            nodo.hijos = [izquierda]

        return nodo

    # ------------------------------------------------------------------
    # Regla: Factor → ~ Factor | ( Exp ) | id
    # ------------------------------------------------------------------

    def _analizar_factor(self) -> NodoDerivacion:
        nodo = NodoDerivacion(simbolo="Factor")

        if self._coincide("~"):
            # Factor → ~ Factor
            self._consumir("~")
            interno = self._analizar_factor()
            nodo.hijos = [NodoDerivacion(simbolo="~"), interno]

        elif self._coincide("("):
            # Factor → ( Exp )
            self._consumir("(")
            exp_interno = self._analizar_exp()

            if not self._coincide(")"):
                posicion = (
                    self._token_actual().posicion
                    if not self._fin_de_entrada()
                    else -1
                )
                raise ErrorSintactico(
                    "Se esperaba ')' para cerrar la expresión entre paréntesis.",
                    posicion=posicion,
                )
            self._consumir(")")
            nodo.hijos = [
                NodoDerivacion(simbolo="("),
                exp_interno,
                NodoDerivacion(simbolo=")"),
            ]

        elif self._coincide("id"):
            # Factor → id
            token = self._avanzar()
            nodo.hijos = [NodoDerivacion(simbolo=token.valor)]

        else:
            if self._fin_de_entrada():
                raise ErrorSintactico(
                    "Fin de expresión inesperado; se esperaba un identificador o '('."
                )
            token = self._token_actual()
            raise ErrorSintactico(
                f"Token inesperado '{token.valor}' en la posición {token.posicion}.",
                posicion=token.posicion,
            )

        return nodo

    # ------------------------------------------------------------------
    # Métodos auxiliares del flujo de tokens
    # ------------------------------------------------------------------

    def _token_actual(self) -> Token:
        return self._tokens[self._pos]

    def _fin_de_entrada(self) -> bool:
        return self._pos >= len(self._tokens)

    def _coincide(self, tipo_esperado: str) -> bool:
        """Retorna True si el token actual es del tipo esperado."""
        if self._fin_de_entrada():
            return False
        return self._tokens[self._pos].tipo == tipo_esperado

    def _avanzar(self) -> Token:
        """Consume y retorna el token actual."""
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _consumir(self, tipo_esperado: str) -> Token:
        """Consume un token del tipo esperado o lanza ErrorSintactico."""
        if self._fin_de_entrada():
            raise ErrorSintactico(
                f"Se esperaba '{tipo_esperado}' pero se llegó al fin de la entrada."
            )
        token = self._token_actual()
        if token.tipo != tipo_esperado:
            raise ErrorSintactico(
                f"Se esperaba '{tipo_esperado}' pero se encontró "
                f"'{token.valor}' en la posición {token.posicion}.",
                posicion=token.posicion,
            )
        return self._avanzar()
