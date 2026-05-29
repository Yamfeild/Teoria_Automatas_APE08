"""Pruebas unitarias para el analizador sintáctico descendente recursivo."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.gramatica.lexer import tokenizar
from app.analizador.parser import AnalizadorSintactico, ErrorSintactico


def _analizar(expresion: str):
    tokens = tokenizar(expresion)
    return AnalizadorSintactico(tokens).analizar()


def prueba_id_simple():
    arbol = _analizar("A")
    assert arbol.simbolo == "Exp"


def prueba_operador_or():
    arbol = _analizar("A | B")
    assert arbol.simbolo == "Exp"
    assert len(arbol.hijos) == 3   # Exp | Term


def prueba_operador_and():
    arbol = _analizar("A & B")
    assert arbol.simbolo == "Exp"


def prueba_operador_not():
    arbol = _analizar("~A")
    assert arbol.simbolo == "Exp"


def prueba_parentesis():
    arbol = _analizar("(A | B)")
    assert arbol.simbolo == "Exp"


def prueba_expresion_compleja():
    arbol = _analizar("A | ~(B & C)")
    assert arbol.simbolo == "Exp"


def prueba_ejemplo_guia_1():
    """Caso de prueba de la guía APE 008: id | ~(id & id)"""
    arbol = _analizar("id | ~(id & id)")
    assert arbol.simbolo == "Exp"


def prueba_ejemplo_guia_2():
    """Caso de prueba de la guía APE 008: A | B & C"""
    arbol = _analizar("A | B & C")
    assert arbol.simbolo == "Exp"


def prueba_operador_doble_invalido():
    try:
        _analizar("A | | B")
        assert False, "Debería lanzar ErrorSintactico"
    except ErrorSintactico:
        pass


def prueba_parentesis_sin_cerrar():
    try:
        _analizar("(A | B")
        assert False, "Debería lanzar ErrorSintactico"
    except ErrorSintactico:
        pass


def prueba_cadena_vacia():
    try:
        _analizar("")
        assert False, "Debería lanzar un error"
    except Exception:
        pass


def prueba_solo_operador():
    try:
        _analizar("|")
        assert False, "Debería lanzar ErrorSintactico"
    except ErrorSintactico:
        pass


def prueba_not_encadenado():
    arbol = _analizar("~~A")
    assert arbol.simbolo == "Exp"


def prueba_precedencia_and_sobre_or():
    """A | B & C debe parsear como A | (B & C), no como (A | B) & C"""
    arbol = _analizar("A | B & C")
    # El hijo derecho del OR debe ser un Term que contiene AND
    assert arbol.simbolo == "Exp"
    assert len(arbol.hijos) == 3
    term_derecho = arbol.hijos[2]   # Term
    assert term_derecho.simbolo == "Term"
    assert len(term_derecho.hijos) == 3   # Term & Factor


# ------------------------------------------------------------------
# Ejecutor de pruebas
# ------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [
        prueba_id_simple,
        prueba_operador_or,
        prueba_operador_and,
        prueba_operador_not,
        prueba_parentesis,
        prueba_expresion_compleja,
        prueba_ejemplo_guia_1,
        prueba_ejemplo_guia_2,
        prueba_operador_doble_invalido,
        prueba_parentesis_sin_cerrar,
        prueba_cadena_vacia,
        prueba_solo_operador,
        prueba_not_encadenado,
        prueba_precedencia_and_sobre_or,
    ]
    aprobadas = 0
    for prueba in pruebas:
        try:
            prueba()
            print(f"  OK    {prueba.__name__}")
            aprobadas += 1
        except AssertionError as e:
            print(f"  FALLA {prueba.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {prueba.__name__}: {e}")
    print(f"\n{aprobadas}/{len(pruebas)} pruebas aprobadas.")
