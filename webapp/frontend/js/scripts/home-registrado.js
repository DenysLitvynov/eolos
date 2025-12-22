// Base de la API (misma raíz para todas las llamadas)
const API_BASE = "/api/v1";

// Helpers de logging con timestamp para depurar fácilmente
const log = (...args) => console.log(new Date().toISOString(), "[home]", ...args);
const err = (...args) => console.error(new Date().toISOString(), "[home:ERR]", ...args);

// Atajo para obtener elementos por id
const $ = (id) => document.getElementById(id);

/**
 * Asigna texto plano a un elemento (evita inyección HTML)
 */
function setText(id, text) {
    const el = $(id);
    if (!el) return;
    el.textContent = text;
}

/**
 * Asigna HTML a un elemento (usar solo con contenido controlado)
 */
function setHTML(id, html) {
    const el = $(id);
    if (!el) return;
    el.innerHTML = html;
}

/**
 * Obtiene la ubicación actual usando Geolocation API.
 * - Devuelve {lat, lon} si se consigue.
 * - Devuelve null si no hay soporte, se deniega o expira el timeout.
 */
function getCurrentPosition() {
    return new Promise((resolve) => {
        if (!navigator.geolocation) return resolve(null);

        navigator.geolocation.getCurrentPosition(
            (pos) => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
            () => resolve(null),
            { enableHighAccuracy: true, timeout: 2500 }
        );
    });
}

/**
 * fetch autenticado usando Bearer token guardado en localStorage.
 * - Lanza error si no existe token.
 * - Añade headers por defecto y permite sobrescribirlos desde options.
 */
async function authFetch(path, options = {}) {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No hay token");

    const url = `${API_BASE}${path}`;
    const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        ...(options.headers || {})
    };

    return fetch(url, { ...options, headers });
}

/**
 * Llama al endpoint /home.
 * - Si hay GPS, añade lat/lon como query params.
 * - Si no hay GPS, llama sin parámetros y el backend hace fallback.
 */
async function apiGetHome() {
    const loc = await getCurrentPosition();
    const qs = loc
        ? `?lat=${encodeURIComponent(loc.lat)}&lon=${encodeURIComponent(loc.lon)}`
        : "";
    return authFetch(`/home${qs}`, { method: "GET" });
}

/**
 * ✅ Ajusta el UI de calidad del aire según el estado:
 * - Cambia clases CSS del score (color)
 * - Cambia la imagen del "smiley"
 */
function applyAirUI(estado) {
    const scoreEl = $("airScore");
    const smileyEl = $("airSmiley");
    if (!scoreEl) return;

    // Limpia clases anteriores para evitar acumulación
    scoreEl.classList.remove("is-good", "is-bad", "is-very-bad");

    const st = (estado || "").toLowerCase().trim();

    // Valores por defecto (amarillo)
    let cls = "is-bad";
    let img = "../images/smiley-yellow.png";

    // Mapeo de estados a estilos/imagen
    if (st === "buena") {
        cls = "is-good";
        img = "../images/smiley-green.png";
    } else if (st === "mala") {
        cls = "is-bad";
        img = "../images/smiley-yellow.png";
    } else if (st === "poco saludable") {
        cls = "is-very-bad";
        img = "../images/smiley-red.png";
    }

    // Aplica la clase final y la imagen final
    scoreEl.classList.add(cls);
    if (smileyEl) smileyEl.src = img;
}

/**
 * Renderiza la lista de gases en <ul id="gasList">
 * - Si no hay gases, muestra un mensaje de fallback.
 */
function renderGases(gases) {
    const ul = $("gasList");
    if (!ul) return;

    // Limpia la lista antes de volver a renderizar
    ul.innerHTML = "";

    // Fallback si no hay datos
    if (!Array.isArray(gases) || gases.length === 0) {
        const li = document.createElement("li");
        li.textContent = "Sin datos de gases para este sensor.";
        ul.appendChild(li);
        return;
    }

    // Pinta cada gas como un <li>
    for (const g of gases) {
        const li = document.createElement("li");
        const tipo = g?.tipo ?? "gas";
        const valor = (g?.valor === null || g?.valor === undefined) ? "-" : g.valor;
        const unidad = g?.unidad ? ` ${g.unidad}` : "";
        li.textContent = `${tipo}: ${valor}${unidad}`;
        ul.appendChild(li);
    }
}

/**
 * Renderiza toda la home con el JSON devuelto por el backend.
 * Actualiza:
 * - Bienvenida (nombre)
 * - AQI (score, estado, descripción)
 * - Gases
 * - Impacto
 * - Último trayecto
 */
function renderHome(data) {
    // Nombre visible del usuario
    setText("welcomeName", data?.usuario?.nombre_visible ?? "—");

    // Calidad del aire (AQI)
    const score = data?.calidad_aire?.score ?? "--";
    const estado = data?.calidad_aire?.estado ?? "--";
    const desc = data?.calidad_aire?.descripcion ?? "—";

    setText("airScore", score);
    setText("airStatus", estado);
    setText("airDesc", desc);

    // Aplica colores/emoji según estado
    applyAirUI(estado);

    // Gases actuales
    renderGases(data?.nivel_actual?.gases);

    // Impacto ambiental (texto)
    setText(
        "impact1",
        `"Has contribuido con ${data?.impacto?.rutas_limpias ?? 0} rutas limpias" • Evitaste ${data?.impacto?.co2_kg ?? 0} kg de CO₂.`
    );
    setText(
        "impact2",
        `"Tienes ${data?.impacto?.puntos ?? 0} puntos para canjear en Velobici".`
    );

    // Último trayecto
    const t = data?.ultimo_trayecto;
    if (!t) {
        // Si no existe trayecto, se muestran valores vacíos
        setHTML("lastTrip", `Distancia: - km<br/>Tiempo: - min<br/>Calidad del aire promedio: -`);
    } else {
        // Formateos básicos para presentar en UI
        const dist = (t.distancia_km == null) ? "-" : Number(t.distancia_km).toFixed(1);
        const tiempo = (t.tiempo_min == null) ? "-" : Math.round(Number(t.tiempo_min));
        setHTML(
            "lastTrip",
            `Distancia: ${dist} km<br/>Tiempo: ${tiempo} min<br/>Calidad del aire promedio: ${t.calidad_promedio ?? "-"}`
        );
    }

    // Debug: placa_id que el backend ha usado para construir datos
    log("placa_id usado:", data?.placa_id);
}

/**
 * Punto de entrada:
 * - Verifica token
 * - Llama a /home (con GPS opcional)
 * - Maneja errores y renderiza UI
 */
async function main() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("No hay token, inicia sesión.");
        window.location.href = "/pages/login.html";
        return;
    }

    try {
        const resp = await apiGetHome();

        // Si el backend devuelve error, registra y lanza excepción
        if (!resp.ok) {
            const text = await resp.text();
            err("GET /home FAIL", resp.status, text);
            throw new Error("No se pudo cargar la home");
        }

        // Parseo del JSON y render
        const data = await resp.json();
        renderHome(data);

    } catch (e) {
        // Manejo centralizado de errores
        err("main()", e);
        alert(e.message || "Error cargando home");
    }
}

// Ejecuta main cuando el DOM ya está cargado
document.addEventListener("DOMContentLoaded", main);
