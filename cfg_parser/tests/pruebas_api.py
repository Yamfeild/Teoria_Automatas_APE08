"""Pruebas unitarias para la capa de servicio y los endpoints de la API."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import crear_app
from app.analizador.servicio import validar_expresion, analizar_expresion


# ------------------------------------------------------------------
# Pruebas de la capa de servicio
# ------------------------------------------------------------------

def prueba_servicio_valida_expresion_correcta():
    resultado = validar_expresion("A | B")
    assert resultado.es_valida is True
    assert resultado.error is None


def prueba_servicio_detecta_expresion_invalida():
    resultado = validar_expresion("A | | B")
    assert resultado.es_valida is False
    assert resultado.error is not None


def prueba_servicio_rechaza_expresion_vacia():
    resultado = validar_expresion("   ")
    assert resultado.es_valida is False


def prueba_servicio_sin_ambiguedad():
    resultado = analizar_expresion("~A")
    assert resultado.es_valida is True
    assert resultado.ambiguedad is not None
    assert resultado.ambiguedad.es_ambigua is False


def prueba_servicio_detecta_ambiguedad():
    resultado = analizar_expresion("A | B & C")
    assert resultado.es_valida is True
    assert resultado.ambiguedad.es_ambigua is True


def prueba_servicio_construye_arbol():
    resultado = analizar_expresion("A | ~(B & C)", construir_arbol=True)
    assert resultado.es_valida is True
    assert resultado.arbol_derivacion is not None
    assert resultado.arbol_derivacion.simbolo == "Exp"


def prueba_servicio_sin_arbol_cuando_no_se_pide():
    resultado = analizar_expresion("A | B", construir_arbol=False)
    assert resultado.arbol_derivacion is None


# ------------------------------------------------------------------
# Pruebas de los endpoints de la API
# ------------------------------------------------------------------

def _cliente():
    app = crear_app()
    app.config["TESTING"] = True
    return app.test_client()


def prueba_api_salud():
    cliente = _cliente()
    respuesta = cliente.get("/api/salud")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["exito"] is True
    assert datos["datos"]["estado"] == "activo"


def prueba_api_gramatica():
    cliente = _cliente()
    respuesta = cliente.get("/api/gramatica")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert "producciones" in datos["datos"]
    assert "no_terminales" in datos["datos"]


def prueba_api_validar_expresion_correcta():
    cliente = _cliente()
    respuesta = cliente.post("/api/validar", json={"expresion": "A | ~B"})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["datos"]["es_valida"] is True


def prueba_api_validar_expresion_incorrecta():
    cliente = _cliente()
    respuesta = cliente.post("/api/validar", json={"expresion": "A | | B"})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["datos"]["es_valida"] is False
    assert datos["datos"]["error"] is not None


def prueba_api_validar_sin_campo_expresion():
    cliente = _cliente()
    respuesta = cliente.post("/api/validar", json={})
    assert respuesta.status_code == 400
    datos = respuesta.get_json()
    assert datos["exito"] is False


def prueba_api_analizar_con_ambiguedad():
    cliente = _cliente()
    respuesta = cliente.post("/api/analizar", json={"expresion": "A | B & C"})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["datos"]["ambiguedad"]["es_ambigua"] is True


def prueba_api_derivar_arbol():
    cliente = _cliente()
    respuesta = cliente.post("/api/derivar", json={"expresion": "A | ~(B & C)"})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["datos"]["es_valida"] is True
    assert datos["datos"]["arbol_derivacion"] is not None
    assert datos["datos"]["arbol_derivacion"]["simbolo"] == "Exp"


def prueba_api_derivar_expresion_invalida():
    cliente = _cliente()
    respuesta = cliente.post("/api/derivar", json={"expresion": "(A | B"})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert datos["datos"]["es_valida"] is False
    assert datos["datos"]["arbol_derivacion"] is None


def prueba_api_derivar_ejemplos_guia():
    """Valida los dos casos de prueba de la guía APE 008."""
    cliente = _cliente()

    # Caso 1: id | ~(id & id)
    r1 = cliente.post("/api/derivar", json={"expresion": "id | ~(id & id)"})
    assert r1.get_json()["datos"]["es_valida"] is True

    # Caso 2: A | B & C
    r2 = cliente.post("/api/derivar", json={"expresion": "A | B & C"})
    d2 = r2.get_json()["datos"]
    assert d2["es_valida"] is True
    assert d2["ambiguedad"]["es_ambigua"] is True


# ------------------------------------------------------------------
# Ejecutor de pruebas
# ------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [
        prueba_servicio_valida_expresion_correcta,
        prueba_servicio_detecta_expresion_invalida,
        prueba_servicio_rechaza_expresion_vacia,
        prueba_servicio_sin_ambiguedad,
        prueba_servicio_detecta_ambiguedad,
        prueba_servicio_construye_arbol,
        prueba_servicio_sin_arbol_cuando_no_se_pide,
        prueba_api_salud,
        prueba_api_gramatica,
        prueba_api_validar_expresion_correcta,
        prueba_api_validar_expresion_incorrecta,
        prueba_api_validar_sin_campo_expresion,
        prueba_api_analizar_con_ambiguedad,
        prueba_api_derivar_arbol,
        prueba_api_derivar_expresion_invalida,
        prueba_api_derivar_ejemplos_guia,
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
