const serverStatus = document.getElementById("server-status");
const statusText = document.getElementById("status-text");
const grammarDefinition = document.getElementById("grammar-definition");
const expressionInput = document.getElementById("expression-input");
const validateBtn = document.getElementById("validate-btn");
const deriveBtn = document.getElementById("derive-btn");
const resultSummary = document.getElementById("result-summary");
const resultMessage = document.getElementById("result-message");
const ambiguityBanner = document.getElementById("ambiguity-banner");
const ambiguityReasons = document.getElementById("ambiguity-reasons");
const treeCanvas = document.getElementById("tree-canvas");
const apiToggle = document.getElementById("api-toggle");
const apiInfoPanel = document.getElementById("api-info-panel");
const SIMBOLOS_TERMINALES = ["id", "|", "&", "~", "(", ")"];

const API_PATHS = {
    salud: "/api/salud",
    gramatica: "/api/gramatica",
    analizar: "/api/analizar",
    derivar: "/api/derivar"
};

let lastEndpointUsed = null;

function setLoadingState(isLoading) {
    validateBtn.disabled = isLoading;
    deriveBtn.disabled = isLoading;
    expressionInput.disabled = isLoading;
}

function toggleApiInfo() {
    apiInfoPanel.classList.toggle("hidden");
}

function updateServerStatus(isActive) {
    const indicator = serverStatus.querySelector(".status-indicator");
    indicator.style.background = isActive ? "#16a34a" : "#dc2626";
    statusText.textContent = isActive ? "Servidor Conectado" : "Servidor No Disponible";
}

function renderGrammar(data) {
    const nonTerminals = data.no_terminales || [];
    const productions = data.producciones || {};
    const terminals = data.terminales || []; 
    const startSymbol = nonTerminals.length ? nonTerminals[0] : "S";

    const productionEntries = Object.entries(productions).map(([lhs, rhs]) => {
        const rules = Array.isArray(rhs) ? rhs : [rhs];
        return `${lhs} → ${rules.join(" | ")}`;
    });

    const sigma = terminals.length ? terminals.join(", ") : "No disponible";
    
    grammarDefinition.textContent = `V = { ${nonTerminals.join(", ")} }\nΣ = { ${sigma} }\nP = {\n  ${productionEntries.join("\n  ")}\n}\nS = ${startSymbol}`;
}

function showResult({ success, message, errorText = null }) {
    ambiguityBanner.classList.add("hidden");
    ambiguityReasons.textContent = "";

    resultMessage.classList.remove("success", "error");
    resultSummary.classList.remove("success", "error");

    // 👇 Eliminamos por completo la variable endpointLabel

    if (success) {
        resultSummary.textContent = "Sintaxis válida";
        resultSummary.classList.add("success");
        // 👇 Imprimimos solo el mensaje limpio
        resultMessage.innerHTML = `<strong>¡Todo correcto!</strong> ${message}`;
        resultMessage.classList.add("success");
    } else {
        resultSummary.textContent = "Error sintáctico";
        resultSummary.classList.add("error");
        // 👇 Imprimimos solo el error limpio
        resultMessage.innerHTML = `<strong>Se encontró un problema:</strong> ${errorText || message}`;
        resultMessage.classList.add("error");
    }
}

function renderTree(node) {
    if (!node || typeof node !== "object") {
        return document.createTextNode("Nodo inválido");
    }

    const symbol = node.simbolo || "?";
    const children = node.hijos;

   let isTerminalVisual = false;

    if (!children || children.length === 0) {
        // Es una hoja Terminal sin hijos (ej ID 'A' o operador '|').
        // Se simplifica visualmente a solo texto estático.
        isTerminalVisual = true;
    } else if (SIMBOLOS_TERMINALES.includes(symbol)) {
        // Aunque tenga hijos (ej parentesis '(' -> hijo 'Exp'), visualmente se comporta como Texto estático.
        isTerminalVisual = true;
    }

    const listItem = document.createElement("li");

    // Creamos la etiqueta del nodo con la clase visual específica decidida arriba
    const nodeLabel = document.createElement("div");
    if (isTerminalVisual) {
        nodeLabel.className = "tree-terminal"; // Clase visual para texto estático azul sutil
    } else {
        nodeLabel.className = "tree-node";     // Clase visual structural boxed pill suave
    }
    nodeLabel.textContent = symbol;
    listItem.appendChild(nodeLabel);

    if (Array.isArray(children) && children.length) {
        const childrenList = document.createElement("ul");
        children.forEach(child => {
            childrenList.appendChild(renderTree(child));
        });
        listItem.appendChild(childrenList);
    }

    return listItem;
}

function drawTree(treeData) {
    treeCanvas.innerHTML = "";
    if (!treeData || typeof treeData !== "object") {
        treeCanvas.innerHTML = `<p class='tree-empty'>No se recibió un árbol válido.</p>`;
        return;
    }

    const rootList = document.createElement("ul");
    rootList.className = "tree-root";
    rootList.appendChild(renderTree(treeData));
    treeCanvas.appendChild(rootList);
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: ${text}`);
    }
    return response.json();
}

async function loadServerStatus() {
    try {
        const result = await fetchJson(API_PATHS.salud);
        const isActive = result?.exito === true && result?.datos?.estado === "activo";
        updateServerStatus(isActive);
    } catch (error) {
        updateServerStatus(false);
        console.error("Error salud API:", error);
    }
}

async function loadGrammar() {
    try {
        const result = await fetchJson(API_PATHS.gramatica);
        if (result?.exito && result?.datos) {
            renderGrammar(result.datos);
        } else {
            grammarDefinition.textContent = "No se pudo cargar la gramática.";
        }
    } catch (error) {
        grammarDefinition.textContent = "Error al cargar la gramática.";
        console.error("Error gramática API:", error);
    }
}

function getExpressionPayload() {
    return {
        expresion: expressionInput.value.trim(),
    };
}

async function submitAction(endpoint, onSuccess) {
    const expression = expressionInput.value.trim();
    if (!expression) {
        showResult({ success: false, message: "Ingresa una expresión booleana antes de continuar." });
        return;
    }

    lastEndpointUsed = endpoint;
    setLoadingState(true);
    try {
        const result = await fetchJson(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getExpressionPayload()),
        });

        const data = result?.datos || {};
        const isValid = data.es_valida === true;
        const errorMessage = data.error; // Aquí viene el mensaje útil: "Token inesperado..."

        if (!isValid) {
            // Pasamos el errorMessage estructurado al frontend
            showResult({ success: false, message: "La expresión no es válida.", errorText: errorMessage });
            treeCanvas.innerHTML = `<p class='tree-empty'>No se generó el árbol por error sintáctico.</p>`;
            return;
        }

        showResult({ success: true, message: "La expresión cumple con la gramática." });
        onSuccess(data);
    } catch (error) {
        showResult({ success: false, message: "Error en la comunicación con el servidor." });
        console.error("Error petición API:", error);
    } finally {
        setLoadingState(false);
    }
}

function procesarAmbiguedad(data) {
    if (data.ambiguedad?.es_ambigua) {
        ambiguityBanner.classList.remove("hidden");
        const reasons = Array.isArray(data.ambiguedad.razones) ? data.ambiguedad.razones.join(" \n") : "Ambigüedad detectada.";
        ambiguityReasons.textContent = reasons;
    } else {
        ambiguityBanner.classList.add("hidden");
        ambiguityReasons.textContent = "";
    }
}

apiToggle.addEventListener("click", toggleApiInfo);

// 3. Botón 1: Llama a /api/analizar (Solo valida y detecta ambigüedad)
validateBtn.addEventListener("click", async () => {
    await submitAction(API_PATHS.analizar, (data) => {
        procesarAmbiguedad(data);
        treeCanvas.innerHTML = `<p class='tree-empty'>El árbol no se genera en este modo para ahorrar recursos.</p>`;
    });
});

// 4. Botón 2: Llama a /api/derivar (Valida, detecta ambigüedad y DIBUJA el árbol)
deriveBtn.addEventListener("click", async () => {
    await submitAction(API_PATHS.derivar, (data) => {
        procesarAmbiguedad(data);
        
        if (data.arbol_derivacion) {
            drawTree(data.arbol_derivacion);
        } else {
            treeCanvas.innerHTML = `<p class='tree-empty'>No se recibió un árbol de derivación válido.</p>`;
        }
    });
});

window.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([loadServerStatus(), loadGrammar()]);
});