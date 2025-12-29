// frontend/js/scripts/home-registrado.js

const API_BASE = "/api/v1";

const log = (...args) => console.log(new Date().toISOString(), "[home]", ...args);
const err = (...args) => console.error(new Date().toISOString(), "[home:ERR]", ...args);

const $ = (id) => document.getElementById(id);

function setText(id, text) {
    const el = $(id);
    if (!el) return;
    el.textContent = text;
}

function setHTML(id, html) {
    const el = $(id);
    if (!el) return;
    el.innerHTML = html;
}

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

async function authFetch(path, options = {}) {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No hay token");

    const url = `${API_BASE}${path}`;
    const headers = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        ...(options.headers || {}),
    };

    return fetch(url, { ...options, headers });
}

async function apiGetHome() {
    const loc = await getCurrentPosition();
    const qs = loc ? `?lat=${encodeURIComponent(loc.lat)}&lon=${encodeURIComponent(loc.lon)}` : "";
    return authFetch(`/home${qs}`, { method: "GET" });
}

function applyAirUI(estado) {
    const scoreEl = $("airScore");
    const smileyEl = $("airSmiley");
    if (!scoreEl) return;

    scoreEl.classList.remove("is-good", "is-bad", "is-very-bad");

    const st = (estado || "").toLowerCase().trim();
    let cls = "is-bad";
    let img = "../images/smiley-yellow.png";

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

    scoreEl.classList.add(cls);
    if (smileyEl) smileyEl.src = img;
}

function renderGases(gases) {
    const ul = $("gasList");
    if (!ul) return;

    ul.innerHTML = "";

    if (!Array.isArray(gases) || gases.length === 0) {
        const li = document.createElement("li");
        li.textContent = "Sin datos de gases para este sensor.";
        ul.appendChild(li);
        return;
    }

    for (const g of gases) {
        const li = document.createElement("li");
        const tipo = g?.tipo ?? "gas";
        const valor = (g?.valor === null || g?.valor === undefined) ? "-" : g.valor;
        const unidad = g?.unidad ? ` ${g.unidad}` : "";
        li.textContent = `${tipo}: ${valor}${unidad}`;
        ul.appendChild(li);
    }
}

function fmtNum(n, digits = 2) {
    if (n === null || n === undefined || Number.isNaN(n)) return "--";
    return Number(n).toFixed(digits);
}

function renderHome(data) {
    setText("welcomeName", data?.usuario?.nombre_visible ?? "—");

    const score = data?.calidad_aire?.score ?? "--";
    const estado = data?.calidad_aire?.estado ?? "--";
    const desc = data?.calidad_aire?.descripcion ?? "—";

    setText("airScore", score);
    setText("airStatus", estado);
    setText("airDesc", desc);

    applyAirUI(estado);
    renderGases(data?.nivel_actual?.gases);

    setText(
        "impact1",
        `"Has contribuido con ${data?.impacto?.rutas_limpias ?? 0} rutas limpias" • Evitaste ${data?.impacto?.co2_kg ?? 0} kg de CO₂.`
    );
    setText("impact2", `"Tienes ${data?.impacto?.puntos ?? 0} puntos para canjear en Velobici".`);

    const t = data?.ultimo_trayecto;
    if (!t) {
        setHTML("lastTrip", `Distancia: - km<br/>Tiempo: - min<br/>Calidad del aire promedio: -`);
    } else {
        const dist = (t.distancia_km == null) ? "-" : Number(t.distancia_km).toFixed(1);
        const tiempo = (t.tiempo_min == null) ? "-" : Math.round(Number(t.tiempo_min));
        setHTML(
            "lastTrip",
            `Distancia: ${dist} km<br/>Tiempo: ${tiempo} min<br/>Calidad del aire promedio: ${t.calidad_promedio ?? "-"}`
        );
    }

    // ✅ KM resumen（从 /home 带回来）
    const km = data?.km_resumen?.km_acumulados ?? 0;
    const descuento = data?.km_resumen?.descuento_acumulado ?? 0;
    const pagaria = data?.km_resumen?.usted_pagaria ?? (data?.km_resumen?.base_price ?? 59.99);

    const kmEl = $("kmValue");
    const discEl = $("discountValue");
    const payEl = $("payValue");

    if (kmEl) kmEl.textContent = `${fmtNum(km, 0)} Km`;
    if (discEl) discEl.textContent = `${fmtNum(descuento, 2)} €`;
    if (payEl) payEl.textContent = `${fmtNum(pagaria, 2)} €`;

    log("placa_id usado:", data?.placa_id);
}

async function main() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("No hay token, inicia sesión.");
        window.location.href = "/pages/login.html";
        return;
    }

    try {
        const resp = await apiGetHome();
        if (!resp.ok) {
            const text = await resp.text();
            err("GET /home FAIL", resp.status, text);
            throw new Error("No se pudo cargar la home");
        }

        const data = await resp.json();
        renderHome(data);
    } catch (e) {
        err("main()", e);
        alert(e.message || "Error cargando home");
    }
}

document.addEventListener("DOMContentLoaded", main);
