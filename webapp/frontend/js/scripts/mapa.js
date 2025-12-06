// File: frontend/js/scripts/mapa.js
/**
 * Autor: Denys Litvynov Lymanets
 * Fecha: 05-12-2025
 * Descripción: Script principal.
 * VISUALIZACIÓN REVERTIDA: Usa la lógica original de radio/blur y colores sólidos.
 * FUNCIONALIDAD: Mantiene soporte para Admin (tabla e historial) y Público (solo hoy).
 */

import { MapaFake } from '../logica_fake/mapa_fake.js';
import { AdminMapasFake } from '../logica_fake/admin_mapas_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    // Detección de si estamos en la página de admin
    const isAdminPage = document.body.classList.contains('admin-map'); // Asegúrate de tener <body class="admin-map"> en el HTML de admin

    const map = L.map('map', {
        zoomControl: false
    }).setView([39.0000, -0.1650], 14);

    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let heatLayer;
    let currentData = { data: {} };

    // Valores por defecto del mapa original
    const defaultLatMin = 38.9800;
    const defaultLonMin = -0.1900;
    const defaultLatMax = 39.0300;
    const defaultLonMax = -0.1400;

    const gasSelect = document.getElementById('gas-select');
    const hourSlider = document.getElementById('hour-slider');
    const hourDisplay = document.getElementById('hour-display');
    const dateFilter = document.getElementById('date-filter');
    const tableBody = document.querySelector('#measures-table tbody');

    // Inicialización
    const currentHour = new Date().getHours();
    hourSlider.value = currentHour;
    hourDisplay.textContent = `${String(currentHour).padStart(2, '0')}:00`;

    const today = new Date().toISOString().split('T')[0];
    if (isAdminPage && dateFilter) dateFilter.value = today;

    // ----------------------------------------------------------
    // LÓGICA VISUAL ORIGINAL (Recuperada de tu primer archivo)
    // ----------------------------------------------------------
    function calculateRadius(zoom) {
        // Ajuste: Aumentar radio con el zoom para fusionar puntos cercanos al acercarse
        // y reducirlo al alejarse para evitar cubrir todo el mapa.
        // Ecuación lineal simple: Zoom 10 -> 10px, Zoom 14 -> 22px, Zoom 18 -> 34px
        return Math.max(5, 10 + (zoom - 10) * 3);
    }

    function calculateBlur(zoom) {
        // Blur proporcional al radio pero un poco menor para mantener definición
        return Math.max(5, calculateRadius(zoom) * 0.7);
    }

    function normalizeIntensity(value, color) {
        // Tu lógica original de intensidades fijas
        if (color === 'verde') return 0.3;
        if (color === 'amarillo') return 0.6;
        return 1.0;
    }

    // ----------------------------------------------------------
    // Obtención de datos
    // ----------------------------------------------------------
    async function updateMapFilters() {
        const selectedGas = gasSelect.value;
        const selectedHour = parseInt(hourSlider.value, 10);
        // Si es admin usa el filtro de fecha, si es público usa "hoy"
        const selectedDate = (isAdminPage && dateFilter) ? dateFilter.value : today;

        // Loading en la tabla (solo admin)
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
            console.error('Error obteniendo datos del mapa:', error);
            if (heatLayer) {
                map.removeLayer(heatLayer);
                heatLayer = null;
            }
            if (isAdminPage && tableBody) {
                tableBody.innerHTML = '<tr><td colspan="6">Error al cargar datos.</td></tr>';
            }
        }
    }

    // ----------------------------------------------------------
    // Mostrar datos en mapa (Lógica Original)
    // ----------------------------------------------------------
    function showHourData(hour) {
        if (!currentData || !currentData.data) return;

        const points = currentData.data[hour] || [];

        if (heatLayer) {
            map.removeLayer(heatLayer);
        }

        const zoom = map.getZoom();
        const heatPoints = points.map(p => [p.lat, p.lng, normalizeIntensity(p.value, p.color)]);

        // Configuración original del HeatLayer
        heatLayer = L.heatLayer(heatPoints, {
            radius: calculateRadius(zoom),
            blur: calculateBlur(zoom),
            gradient: { 0.0: 'green', 0.5: 'yellow', 1.0: 'red' } // Gradiente original sólido
        }).addTo(map);
    }

    // ----------------------------------------------------------
    // Poblar Tabla (Funcionalidad Nueva para Admin)
    // ----------------------------------------------------------
    function populateTable(hour) {
        if (!tableBody) return;
        tableBody.innerHTML = '';

        const points = (currentData.data && currentData.data[hour]) ? currentData.data[hour] : [];

        if (points.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6">No hay medidas disponibles.</td></tr>';
            return;
        }

        // Usamos Fragment para que sea rápido
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
                <td style="color:${getColorCss(p.color)}; font-weight:bold;">${p.color.toUpperCase()}</td>
            `;
            fragment.appendChild(tr);
        });
        tableBody.appendChild(fragment);
    }

    function getColorCss(color) {
        if (color === 'verde') return 'green';
        if (color === 'amarillo') return '#DAA520'; // GoldenRod para que se lea mejor
        if (color === 'rojo') return 'red';
        return 'black';
    }

    // ----------------------------------------------------------
    // Listeners
    // ----------------------------------------------------------
    gasSelect.addEventListener('change', updateMapFilters);

    if (isAdminPage && dateFilter) {
        dateFilter.addEventListener('change', updateMapFilters);
    }

    hourSlider.addEventListener('input', (e) => {
        const hour = e.target.value;
        hourDisplay.textContent = `${hour.padStart(2, '0')}:00`;
        showHourData(hour); // Renderizado directo, sin debounce
        if (isAdminPage) populateTable(hour);
    });

    // Evento zoom original
    map.on('zoomend moveend', () => {
        const hour = hourSlider.value;
        showHourData(hour);
    });

    // Carga inicial
    updateMapFilters();
});
