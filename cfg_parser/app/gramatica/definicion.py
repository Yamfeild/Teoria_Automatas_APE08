"""
Definición formal de la Gramática Libre de Contexto (CFG) para expresiones booleanas.

Gramática G = (V, Σ, P, S):

  V  = { Exp, Term, Factor }       — símbolos no terminales
  Σ  = { id, |, &, ~, (, ) }      — símbolos terminales
  S  = Exp                         — símbolo inicial
  P  = reglas de producción (ver abajo)

Reglas de producción (P) con precedencia codificada estructuralmente:

  Nivel 1 — OR  (menor precedencia):
      Exp    → Exp | Term
      Exp    → Term

  Nivel 2 — AND (precedencia media):
      Term   → Term & Factor
      Term   → Factor

  Nivel 3 — NOT / Base (mayor precedencia):
      Factor → ~ Factor
      Factor → ( Exp )
      Factor → id
"""

DEFINICION_GRAMATICA = {
    "no_terminales": ["Exp", "Term", "Factor"],
    "terminales": ["id", "|", "&", "~", "(", ")"],
    "simbolo_inicial": "Exp",
    "producciones": {
        "Exp": [
            ["Exp", "|", "Term"],
            ["Term"],
        ],
        "Term": [
            ["Term", "&", "Factor"],
            ["Factor"],
        ],
        "Factor": [
            ["~", "Factor"],
            ["(", "Exp", ")"],
            ["id"],
        ],
    },
}
