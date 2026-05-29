# CFG Parser — Backend
### Analizador de Gramáticas Libres de Contexto para Expresiones Booleanas

Proyecto desarrollado en Python + Flask como parte de la Pràctica Nùmero 8: Construcción y Validación de Gramáticas Libres de Contexto.  
Asignatura: Teoría de Autómatas y Computabilidad Avanzada.

---

## Gramática implementada

```
G = (V, Σ, P, S)

V  = { Exp, Term, Factor }       — no terminales
Σ  = { id, |, &, ~, (, ) }       — terminales
S  = Exp                         — símbolo inicial

Producciones (P):
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
```

---

## Estructura del proyecto

```
cfg_parser/
│
├── run.py                          ← Punto de entrada — ejecutar esto
├── requirements.txt                ← Dependencias del proyecto
│
├── app/
│   ├── __init__.py                 ← Fábrica de la aplicación (crear_app)
│   │
│   ├── gramatica/                  ← Definición formal y análisis léxico
│   │   ├── __init__.py
│   │   ├── definicion.py           ← G = (V, Σ, P, S) como diccionario
│   │   └── lexer.py                ← Analizador léxico / tokenizador
│   │
│   ├── analizador/                 ← Núcleo del análisis sintáctico
│   │   ├── __init__.py
│   │   ├── arbol.py                ← NodoDerivacion — árbol de derivación
│   │   ├── parser.py               ← AnalizadorSintactico descendente recursivo
│   │   ├── ambiguedad.py           ← Detector de ambigüedad gramatical
│   │   └── servicio.py             ← Capa de servicio (orquesta todo)
│   │
│   └── api/
│       ├── __init__.py
│       ├── rutas.py                ← Endpoints Flask
│       └── respuestas.py           ← Helpers para respuestas JSON uniformes
│
└── tests/
    ├── __init__.py
    ├── pruebas_lexer.py            ← 10 pruebas del analizador léxico
    ├── pruebas_parser.py           ← 14 pruebas del analizador sintáctico
    └── pruebas_api.py              ← 16 pruebas de servicios y endpoints
```

---

## Instalación y ejecución

### 1. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Iniciar el servidor

```bash
python run.py
```

Servidor disponible en: `http://localhost:5000`

### 4. Ejecutar pruebas

```bash
python tests/pruebas_lexer.py
python tests/pruebas_parser.py
python tests/pruebas_api.py
```

---

## Endpoints de la API

Todas las respuestas siguen este envelope uniforme:

```json
{
  "exito":  true | false,
  "datos":  { ... } | null,
  "error":  null   | "mensaje de error"
}
```

---

### `GET /api/salud`
Verifica que el servidor esté activo.

```json
{
  "exito": true,
  "datos": { "estado": "activo", "mensaje": "CFG Parser API en funcionamiento." },
  "error": null
}
```

---

### `GET /api/gramatica`
Retorna la definición formal de la gramática G = (V, Σ, P, S).

```json
{
  "exito": true,
  "datos": {
    "no_terminales": ["Exp", "Term", "Factor"],
    "terminales": ["id", "|", "&", "~", "(", ")"],
    "simbolo_inicial": "Exp",
    "producciones": { ... }
  },
  "error": null
}
```

---

### `POST /api/validar`
Valida si la cadena pertenece al lenguaje de la gramática.

**Cuerpo:**
```json
{ "expresion": "A | ~(B & C)" }
```

**Respuesta — cadena válida:**
```json
{
  "exito": true,
  "datos": {
    "expresion": "A | ~(B & C)",
    "es_valida": true,
    "error": null,
    "posicion_error": null
  },
  "error": null
}
```

**Respuesta — cadena inválida:**
```json
{
  "exito": true,
  "datos": {
    "expresion": "A | | B",
    "es_valida": false,
    "error": "Token inesperado '|' en la posición 4.",
    "posicion_error": 4
  },
  "error": null
}
```

---

### `POST /api/analizar`
Validación + detección de ambigüedad gramatical.

**Cuerpo:**
```json
{ "expresion": "A | B & C" }
```

**Respuesta:**
```json
{
  "exito": true,
  "datos": {
    "expresion": "A | B & C",
    "es_valida": true,
    "error": null,
    "posicion_error": null,
    "ambiguedad": {
      "es_ambigua": true,
      "razones": [
        "La expresión mezcla operadores '|' (OR) y '&' (AND) en el mismo nivel..."
      ]
    }
  },
  "error": null
}
```

---

### `POST /api/derivar`
Validación + ambigüedad + **árbol de derivación por la izquierda**.

**Cuerpo:**
```json
{ "expresion": "A | ~(B & C)" }
```

**Respuesta:**
```json
{
  "exito": true,
  "datos": {
    "expresion": "A | ~(B & C)",
    "es_valida": true,
    "error": null,
    "posicion_error": null,
    "ambiguedad": { "es_ambigua": false, "razones": [] },
    "arbol_derivacion": {
      "simbolo": "Exp",
      "hijos": [
        { "simbolo": "Exp",  "hijos": [...] },
        { "simbolo": "|",    "hijos": [] },
        { "simbolo": "Term", "hijos": [...] }
      ]
    }
  },
  "error": null
}
```

---

## Pruebas con Thunder Client

Crear las siguientes peticiones (header requerido: `Content-Type: application/json`):

| Método | URL | Body |
|--------|-----|------|
| GET  | `http://localhost:5000/api/salud`    | — |
| GET  | `http://localhost:5000/api/gramatica` | — |
| POST | `http://localhost:5000/api/validar`  | `{"expresion": "id | ~(id & id)"}` |
| POST | `http://localhost:5000/api/analizar` | `{"expresion": "A | B & C"}` |
| POST | `http://localhost:5000/api/derivar`  | `{"expresion": "A | ~(B & C)"}` |

---

## Casos de prueba de la guía APE 008

| Expresión          | ¿Válida? | ¿Ambigua? | Descripción |
|--------------------|----------|-----------|-------------|
| `id \| ~(id & id)` | ✅ Sí    | ❌ No     | Ejemplo 1 de la guía |
| `A \| B & C`       | ✅ Sí    | ✅ Sí     | Ejemplo 2 de la guía |
| `A \| \| B`        | ❌ No    | —         | Operador doble inválido |
| `~~A`              | ✅ Sí    | ❌ No     | NOT encadenado |
| `(A \| B) & C`     | ✅ Sí    | ❌ No     | Agrupación explícita |

---

## Nota para el equipo de frontend

- **CORS** habilitado para todos los orígenes mediante `flask-cors`.
- El `arbol_derivacion` llega como JSON anidado con campos `simbolo` y `hijos[]`, listo para renderizar con **D3.js**, **vis.js**, o cualquier librería de árboles.
- Los campos de respuesta están en español para mantener consistencia con el proyecto académico.
