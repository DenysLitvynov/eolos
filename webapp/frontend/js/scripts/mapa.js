/**
 * Autores:Hugo Belda y Denys Litvynov 
 * Fecha: 05-12-2025
 * Descripción: Script principal.
 */

import { MapaFake } from '../logica_fake/mapa_fake.js';
import { AdminMapasFake } from '../logica_fake/admin_mapas_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const isAdminPage = document.body.classList.contains('admin-map');

    const map = L.map('map', {
        zoomControl: false
    }).setView([39.0000, -0.1650], 14);

    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        crossOrigin: ''
    }).addTo(map);

    let heatLayer;
    let currentData = { data: {} };

    // RECTÁNGULO COMPLETO DE PLATJA I GRAU DE GANDIA
    const defaultLatMin = 38.9865;
    const defaultLonMin = -0.1735;
    const defaultLatMax = 39.0035;
    const defaultLonMax = -0.1485;

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

    const FIXED_RADIUS = 28;
    const FIXED_BLUR = 22;

    function fixedIntensity(color) {
        if (color === 'verde') return 0.40;
        if (color === 'amarillo') return 0.70;
        return 1.00; // rojo
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
            if (heatLayer) map.removeLayer(heatLayer);
            if (isAdminPage && tableBody) {
                tableBody.innerHTML = '<tr><td colspan="6">Error al cargar datos.</td></tr>';
            }
        }
    }

    // ==========================================================
    // PINTAR CAPA DE CALOR ESTABLE
    // ==========================================================
    function showHourData(hour) {
        if (!currentData || !currentData.data) return;

        const points = currentData.data[hour] || [];

        if (heatLayer) map.removeLayer(heatLayer);

        const heatPoints = points.map(p => [
            p.lat,
            p.lng,
            fixedIntensity(p.color) // intensidad basada SOLO en color
        ]);

        // HeatLayer CON PARAMETROS FIJOS
        heatLayer = L.heatLayer(heatPoints, {
            radius: FIXED_RADIUS,
            blur: FIXED_BLUR,
            gradient: {
                0.0: 'green',
                0.5: 'yellow',
                1.0: 'red'
            }
        }).addTo(map);
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
        if (color === 'verde') return 'green';
        if (color === 'amarillo') return '#DAA520';
        if (color === 'rojo') return 'red';
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
        const hour = e.target.value;
        hourDisplay.textContent = `${hour.padStart(2, '0')}:00`;
        showHourData(hour);
        if (isAdminPage) populateTable(hour);
    });

    updateMapFilters();
});
