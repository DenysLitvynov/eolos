// frontend/js/scripts/pollution.js
(function () {
    const API_BASE = "/api/v1";

    const log = (...args) => console.log(new Date().toISOString(), "[pollution]", ...args);
    const err = (...args) => console.error(new Date().toISOString(), "[pollution:ERR]", ...args);

    function dotClassFromColor(color) {
        if (!color) return "yellow";
        const c = String(color).toLowerCase();
        if (c.includes("rojo")) return "red";
        if (c.includes("verde")) return "green";
        if (c.includes("amar")) return "yellow";
        return "yellow";
    }

    function labelFromDotClass(dot) {
        if (dot === "red") return "rojo";
        if (dot === "green") return "verde";
        return "amarillo";
    }

    function liHTML(item) {
        const nombre = item?.nombre ?? "Estación";
        const color = item?.medicion?.color ?? null;

        const dot = dotClassFromColor(color);
        const etiqueta = labelFromDotClass(dot);

        return `<li><span class="dot ${dot}"></span> Nodo en ${etiqueta}: ${nombre}</li>`;
    }

    async function fetchContaminacion(limit = 10) {
        const url = `${API_BASE}/contaminacion/estaciones?limit=${encodeURIComponent(limit)}`;
        const resp = await fetch(url, { method: "GET" });
        if (!resp.ok) {
            const text = await resp.text().catch(() => "");
            throw new Error(`HTTP ${resp.status} ${text}`);
        }
        return resp.json();
    }

    async function render() {
        const $left = document.getElementById("pollution-left");
        const $right = document.getElementById("pollution-right");
        const $meta = document.getElementById("pollution-meta");

        // 页面没有污染模块就直接退出（不会报错，可复用）
        if (!$left || !$right) return;

        $left.innerHTML = "";
        $right.innerHTML = "";
        if ($meta) $meta.textContent = "Cargando...";

        try {
            const data = await fetchContaminacion(10);
            log("data", data);

            const items = Array.isArray(data?.items) ? data.items : [];
            const half = Math.ceil(items.length / 2);

            $left.innerHTML = items.slice(0, half).map(liHTML).join("");
            $right.innerHTML = items.slice(half).map(liHTML).join("");

            if ($meta) $meta.textContent = "";
        } catch (e) {
            err("render()", e);
            if ($meta) $meta.textContent = "Error cargando datos.";
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        render();

        const btn = document.getElementById("btn-pollution-refresh");
        if (btn) {
            btn.addEventListener("click", (ev) => {
                ev.preventDefault();
                render();
            });
        }
    });
})();
