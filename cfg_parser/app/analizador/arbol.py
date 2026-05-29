"""
Estructura del Árbol de Derivación.

Un NodoDerivacion representa un nodo dentro del árbol de derivación
(parse tree) producido por el analizador sintáctico.

Cada nodo almacena:
  - simbolo  : el símbolo de la gramática (terminal o no terminal)
  - hijos    : lista ordenada de nodos hijos (vacía en nodos hoja)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class NodoDerivacion:
    """Un nodo dentro del árbol de derivación (parse tree)."""

    simbolo: str
    hijos: List[NodoDerivacion] = field(default_factory=list)

    @property
    def es_hoja(self) -> bool:
        """Retorna True cuando el nodo es terminal (no tiene hijos)."""
        return len(self.hijos) == 0

    def a_dict(self) -> dict:
        """
        Serializa el árbol en un diccionario anidado para respuestas JSON.

        Formato de salida:
            {
                "simbolo": "Exp",
                "hijos": [
                    { "simbolo": "Term", "hijos": [...] }
                ]
            }
        """
        return {
            "simbolo": self.simbolo,
            "hijos": [hijo.a_dict() for hijo in self.hijos],
        }
