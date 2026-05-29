"""Pruebas unitarias para el analizador léxico."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.gramatica.lexer import tokenizar, ErrorLexico


def prueba_id_simple():
    tokens = tokenizar("A")
    assert len(tokens) == 1
    assert tokens[0].tipo == "id"
    assert tokens[0].valor == "A"


def prueba_expresion_or():
    tokens = tokenizar("A | B")
    tipos = [t.tipo for t in tokens]
    assert tipos == ["id", "|", "id"]


def prueba_expresion_and():
    tokens = tokenizar("A & B")
    tipos = [t.tipo for t in tokens]
    assert tipos == ["id", "&", "id"]


def prueba_expresion_not():
    tokens = tokenizar("~A")
    tipos = [t.tipo for t in tokens]
    assert tipos == ["~", "id"]


def prueba_expresion_compleja():
    tokens = tokenizar("A | ~(B & C)")
    tipos = [t.tipo for t in tokens]
    assert tipos == ["id", "|", "~", "(", "id", "&", "id", ")"]


def prueba_ignora_espacios():
    tokens = tokenizar("  A   |   B  ")
    assert len(tokens) == 3


def prueba_identificador_multicaracter():
    tokens = tokenizar("miVar | otraVar")
    assert tokens[0].valor == "miVar"
    assert tokens[2].valor == "otraVar"


def prueba_caracter_invalido():
    try:
        tokenizar("A @ B")
        assert False, "Debería lanzar ErrorLexico"
    except ErrorLexico as e:
        assert e.caracter == "@"


def prueba_cadena_vacia():
    tokens = tokenizar("")
    assert tokens == []


def prueba_rastreo_posicion():
    tokens = tokenizar("A | B")
    assert tokens[0].posicion == 0
    assert tokens[1].posicion == 2
    assert tokens[2].posicion == 4


# ------------------------------------------------------------------
# Ejecutor de pruebas
# ------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [
        prueba_id_simple,
        prueba_expresion_or,
        prueba_expresion_and,
        prueba_expresion_not,
        prueba_expresion_compleja,
        prueba_ignora_espacios,
        prueba_identificador_multicaracter,
        prueba_caracter_invalido,
        prueba_cadena_vacia,
        prueba_rastreo_posicion,
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
