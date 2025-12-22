/**
 * Autores:Hugo Belda y Denys Litvynov Lymanets 
 * Fecha: 05-12-2025
 * Descripción: Script principal.
 */

import { MapaFake } from '../logica_fake/mapa_fake.js';
import { AdminMapasFake } from '../logica_fake/admin_mapas_fake.js';
import { cargarEstacionesDesdeApi } from './estaciones_api.js';
import { cargarEstacionesBicicletas } from './bicicletas.js';

// ==========================================================
// CANVAS OVERLAY PLUGIN (para capa fija) - COPIADO DEL EJEMPLO
// ==========================================================
L.CanvasOverlay = (L.Layer ? L.Layer : L.Class).extend({
    initialize: function (userDrawFunc, options) {
        this._userDrawFunc = userDrawFunc;
        L.setOptions(this, options);
    },

    drawing: function (userDrawFunc) {
        this._userDrawFunc = userDrawFunc;
        return this;
    },

    canvas: function () { return this._canvas; },

    onAdd: function (map) {
        this._map = map;
        this._canvas = L.DomUtil.create("canvas", "leaflet-canvas-overlay");
        const size = map.getSize();
        this._canvas.width = size.x;
        this._canvas.height = size.y;
        map.getPanes().overlayPane.appendChild(this._canvas);

        map.on("moveend zoomend resize", this._reset, this);
        this._reset();
    },

    onRemove: function (map) {
        const pane = map.getPanes().overlayPane;
        if (this._canvas && pane.contains(this._canvas))
            pane.removeChild(this._canvas);

        map.off("moveend zoomend resize", this._reset, this);
    },

    addTo: function (map) {
        map.addLayer(this);
        return this;
    },

    _reset: function () {
        if (!this._map || !this._canvas || !this._userDrawFunc) return;

        const topLeft = this._map.containerPointToLayerPoint([0, 0]);
        L.DomUtil.setPosition(this._canvas, topLeft);

        const size = this._map.getSize();
        this._canvas.width = size.x;
        this._canvas.height = size.y;

        this._userDrawFunc(this, {
            canvas: this._canvas,
            bounds: this._map.getBounds(),
            size: size,
            zoom: this._map.getZoom()
        });
    }
});

L.canvasOverlay = (fn, options) => new L.CanvasOverlay(fn, options);

// ==========================================================
// COLORES FIJOS BASADOS EN CALIDAD - COINCIDENTES CON TU EJEMPLO
// ==========================================================
function colorPorCalidad(color) {
    switch (color) {
        case 'verde': return [84, 226, 73];    // #54E249 - VERDE
        case 'amarillo': return [255, 247, 27]; // #FFF71B - AMARILLO
        case 'rojo': return [255, 48, 48];     // #FF3030 - ROJO (igual que en ejemplo)
        default: return [84, 226, 73]; // Por defecto verde
    }
}

// ==========================================================
// FUNCIÓN PARA NORMALIZAR VALORES A NIVELES (0-1)
// ==========================================================
function normalizarValor(tipo, valor) {
    // Rangos aproximados para normalización
    // Puedes ajustar estos valores según tus necesidades
    if (valor <= 50) return 0.1;      // Verde
    if (valor <= 100) return 0.45;    // Amarillo
    return 1.0;                       // Rojo
}

document.addEventListener('DOMContentLoaded', () => {
    const isAdminPage = document.body.classList.contains('admin-map');

    const map = L.map('map', {
        zoomControl: false
    }).setView([39.47, -0.3763], 13); // Valencia por defecto

    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        crossOrigin: ''
    }).addTo(map);

    let puntosActuales = [];
    let canvasLayer = null;
    let currentData = { data: {} };

    // RECTÁNGULO DE VALENCIA
    const defaultLatMin = 39.44;
    const defaultLonMin = -0.42;
    const defaultLatMax = 39.50;
    const defaultLonMax = -0.34;

    const gasSelect = document.getElementById('gas-select');
    const hourSlider = document.getElementById('hour-slider');
    const hourDisplay = document.getElementById('hour-display');
    const dateFilter = document.getElementById('date-filter');
    const tableBody = document.querySelector('#measures-table tbody');

    // Sidebar Toggle (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // Inicialización
    const currentHour = new Date().getHours();
    hourSlider.value = currentHour;
    hourDisplay.textContent = `${String(currentHour).padStart(2, '0')}:00`;

    const today = new Date().toISOString().split('T')[0];
    if (isAdminPage && dateFilter) dateFilter.value = today;

    // ==========================================================
    // FUNCIÓN IDW – CUADRÍCULA CONTINUA (sin bordes visibles)
    // ==========================================================
    function dibujarIDW(layer, params) {
        const canvas = params.canvas;
        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (!puntosActuales.length) return;

        // Parámetros visuales
        const RADIO = 0.015;
        const GRID = 90;        // ↑ más celdas → menos efecto mosaico
        const EXP = 2;
        const ALPHA = 0.2;      // ligera subida para fusionar celdas
        const RATIO = 1.15;     // solape entre cuadraditos

        const stepX = canvas.width / GRID;
        const stepY = canvas.height / GRID;

        ctx.imageSmoothingEnabled = true;
        ctx.globalCompositeOperation = 'source-over';

        for (let ix = 0; ix < GRID; ix++) {
            for (let iy = 0; iy < GRID; iy++) {

                const px = ix * stepX + stepX / 2;
                const py = iy * stepY + stepY / 2;

                const ll = map.containerPointToLatLng([px, py]);
                const lat = ll.lat;
                const lng = ll.lng;

                let sumW = 0, sumR = 0, sumG = 0, sumB = 0;

                // IDW
                for (let p of puntosActuales) {
                    const dx = lng - p.lng;
                    const dy = lat - p.lat;
                    const d = Math.sqrt(dx * dx + dy * dy);

                    if (d > RADIO) continue;

                    const w = (d === 0) ? 1 : 1 / Math.pow(d, EXP);

                    sumW += w;
                    sumR += w * p.r;
                    sumG += w * p.g;
                    sumB += w * p.b;
                }

                if (sumW === 0) continue;

                const r = sumR / sumW;
                const g = sumG / sumW;
                const b = sumB / sumW;

                ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${ALPHA})`;

                // ⚠️ solape real para eliminar costuras
                ctx.fillRect(
                    ix * stepX - stepX * 0.075,
                    iy * stepY - stepY * 0.075,
                    stepX * RATIO,
                    stepY * RATIO
                );
            }
        }
    }


    
    async function updateMapFilters() {
        const selectedGas = gasSelect.value;
        const selectedHour = parseInt(hourSlider.value, 10);
        const selectedDate = (isAdminPage && dateFilter) ? dateFilter.value : today;

        if (isAdminPage && tableBody) {
            tableBody.innerHTML = '<tr><td colspan="6">Cargando datos...</td></tr>';
        }

        try {
            let respuesta;
            if (isAdminPage) {
                const adminFake = new AdminMapasFake();
                respuesta = await adminFake.obtenerMapaAdmin(
                    selectedGas, selectedDate, defaultLatMin, defaultLonMin, defaultLatMax, defaultLonMax
                );
            } else {
                const mapaFake = new MapaFake();
                respuesta = await mapaFake.obtenerMapa(
                    selectedGas, today, defaultLatMin, defaultLonMin, defaultLatMax, defaultLonMax
                );
            }

            currentData = respuesta;
            showHourData(selectedHour);

            if (isAdminPage) populateTable(selectedHour);

        } catch (error) {
            console.error('Error obteniendo datos:', error);
            puntosActuales = [];
            currentData = { data: {} };
            if (canvasLayer) {
                canvasLayer._reset();
            }
            if (isAdminPage && tableBody) {
                tableBody.innerHTML = '<tr><td colspan="6">Error al cargar datos.</td></tr>';
            }
        }
    }

    // ==========================================================
    // ACTUALIZAR DATOS PARA UNA HORA
    // ==========================================================
    function showHourData(hour) {
        if (!currentData || !currentData.data) {
            puntosActuales = [];
            if (canvasLayer) {
                canvasLayer._reset();
            }
            return;
        }

        const points = currentData.data[hour] || [];
        
        // Convertir puntos a formato para interpolación IDW
        puntosActuales = points.map(p => {
            const [r, g, b] = colorPorCalidad(p.color);
            return { 
                lat: p.lat, 
                lng: p.lng, 
                r, g, b,
                valor: p.value,
                color: p.color
            };
        });

        // Crear o actualizar la capa canvas
        if (!canvasLayer) {
            canvasLayer = L.canvasOverlay(dibujarIDW).addTo(map);
        } else {
            canvasLayer._reset();
        }
    }

    // ==========================================================
    // Poblar tabla (solo admin)
    // ==========================================================
    function populateTable(hour) {
        if (!tableBody) return;

        tableBody.innerHTML = '';
        const points = currentData.data[hour] || [];

        if (points.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6">No hay medidas.</td></tr>';
            return;
        }

        const fragment = document.createDocumentFragment();

        points.forEach(p => {
            const tipo = gasSelect.options[gasSelect.selectedIndex].text;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${String(hour).padStart(2, '0')}:00</td>
                <td>${p.lat.toFixed(4)}</td>
                <td>${p.lng.toFixed(4)}</td>
                <td>${tipo}</td>
                <td>${p.value.toFixed(2)}</td>
                <td style="color:${getColorCss(p.color)}; font-weight:bold;">
                    ${p.color.toUpperCase()}
                </td>
            `;
            fragment.appendChild(tr);
        });

        tableBody.appendChild(fragment);
    }

    function getColorCss(color) {
        if (color === 'verde') return '#54E249';
        if (color === 'amarillo') return '#FFF71B';
        if (color === 'rojo') return '#FF3030';
        return 'black';
    }

    // ==========================================================
    // EVENTOS
    // ==========================================================
    gasSelect.addEventListener('change', updateMapFilters);

    if (isAdminPage && dateFilter) {
        dateFilter.addEventListener('change', updateMapFilters);
    }

    hourSlider.addEventListener('input', (e) => {
        const hour = parseInt(e.target.value, 10);
        hourDisplay.textContent = `${hour.toString().padStart(2, '0')}:00`;
        showHourData(hour);
        if (isAdminPage) populateTable(hour);
    });

    // Filtros de capas
    const bikesCheckbox = document.getElementById('layer-bikes');
    const pollutionCheckbox = document.getElementById('layer-pollution');
    let bikesLayer = null;
    let pollutionLayer = null;

    async function initLayers() {
        // Cargar capas
        bikesLayer = await cargarEstacionesBicicletas();
        pollutionLayer = await cargarEstacionesDesdeApi();

        // Estado inicial
        if (bikesCheckbox.checked && bikesLayer) {
            bikesLayer.addTo(map);
        }
        if (pollutionCheckbox.checked && pollutionLayer) {
            pollutionLayer.addTo(map);
        }

        // Listeners
        bikesCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                if (bikesLayer) bikesLayer.addTo(map);
            } else {
                if (bikesLayer) map.removeLayer(bikesLayer);
            }
        });

        pollutionCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                if (pollutionLayer) pollutionLayer.addTo(map);
            } else {
                if (pollutionLayer) map.removeLayer(pollutionLayer);
            }
        });
    }

    // Redibujar al mover/zoom
    map.on('moveend zoomend', () => {
        if (canvasLayer) {
            canvasLayer._reset();
        }
    });

    // Inicializar
    updateMapFilters();
    initLayers();
});
