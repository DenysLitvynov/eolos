// File: frontend/js/scripts/mapa.js (COMPLETO y CORREGIDO)
import { MapaFake } from '../logica_fake/mapa_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar mapa
    const map = L.map('map', {
        zoomControl: false
    }).setView([39.0000, -0.1650], 14); // CAMBIO 1: Centrado en Grau de Gandia

    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let heatLayer;

    // CAMBIO 2: Bounds fijos para Grau i Platja de Gandia
    const defaultLatMin = 38.9800; 
    const defaultLonMin = -0.1900; 
    const defaultLatMax = 39.0300; 
    const defaultLonMax = -0.1400; 

    // Date Filter Listener
    const dateFilter = document.getElementById('date-filter');
    if (dateFilter) {
        // Set default to today
        const today = new Date().toISOString().split('T')[0];
        dateFilter.value = today;

        dateFilter.addEventListener('change', updateMapFilters);
    }

    // Gas Select Listener
    const gasSelect = document.getElementById('gas-select');
    if (gasSelect) {
        gasSelect.addEventListener('change', updateMapFilters);
    }

    // Hour Slider
    const hourSlider = document.getElementById('hour-slider');
    const hourDisplay = document.getElementById('hour-display');
    if (hourSlider && hourDisplay) {
        hourSlider.addEventListener('input', (e) => {
            const hour = e.target.value;
            hourDisplay.textContent = `${hour.padStart(2, '0')}:00`;
            showHourData(hour);
        });
        // Initial set of hour
        const initialHour = hourSlider.value.padStart(2, '0');
        hourDisplay.textContent = `${initialHour}:00`;
    }

    let currentData = { data: {} }; // Inicializar con estructura esperada

    // Mapeo de tipos
    function mapTipo(selected) {
        if (selected === 'pm25') return 'pm2_5';
        return selected;
    }

    async function updateMapFilters() {
        const selectedGas = gasSelect ? mapTipo(gasSelect.value) : 'general';
        const selectedDate = dateFilter ? dateFilter.value : new Date().toISOString().split('T')[0];
        const selectedHour = hourSlider ? parseInt(hourSlider.value, 10) : 12;

        console.log(`Actualizando mapa... Gas: ${selectedGas}, Fecha: ${selectedDate}, Hora: ${selectedHour}:00`);

        const mapaFake = new MapaFake();

        // Asegúrate de pasar TODOS los bounds como números
        const lat_min = defaultLatMin;
        const lon_min = defaultLonMin;
        const lat_max = defaultLatMax;
        const lon_max = defaultLonMax;

        try {
            currentData = await mapaFake.obtenerMapa(
                selectedGas,
                selectedDate,
                lat_min,
                lon_min,
                lat_max,
                lon_max
            );
            showHourData(selectedHour);
        } catch (error) {
            console.error('Error obteniendo datos del mapa:', error);
            if (heatLayer) {
                map.removeLayer(heatLayer);
                heatLayer = null;
            }
        }
    }

    function showHourData(hour) {
        if (!currentData) return;
        const points = currentData.data[hour] || [];
        if (heatLayer) {
            map.removeLayer(heatLayer);
        }
        const heatPoints = points.map(p => [p.lat, p.lng, normalizeIntensity(p.value, p.color)]);
        heatLayer = L.heatLayer(heatPoints, {
            radius: 25,
            blur: 15,
            gradient: {0.0: 'green', 0.5: 'yellow', 1.0: 'red'}
        }).addTo(map);
    }

    function addHeatLayer(points) {
        if (heatLayer) {
            map.removeLayer(heatLayer);
        }
        
        // El punto de calor se genera con [lat, lng, intensidad]
        const heatPoints = points.map(p => [p.lat, p.lng, normalizeIntensity(p.value, p.color)]);
        
        heatLayer = L.heatLayer(heatPoints, {
            radius: 35,   // CAMBIO 3: Aumentado para mayor densidad
            blur: 20,     // CAMBIO 4: Aumentado para mayor difuminado
            gradient: {0.0: 'green', 0.5: 'yellow', 1.0: 'red'}
        }).addTo(map);
    }

    function normalizeIntensity(value, color) {
        // Normalizar a 0-1 basado en color/value (usando el valor AQI del backend)
        if (color === 'verde') return 0.3;
        if (color === 'amarillo') return 0.6;
        return 1.0;
    }

    // Initial load
    updateMapFilters();

    // Sidebar Toggle (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
});

const header = document.querySelector('.header');
if (header) {
    const nav = header.querySelector('.nav');
    const btn = header.querySelector('.menu-toggle');

    function closeMenu() {
        btn.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
    }

    function openMenu() {
        btn.setAttribute('aria-expanded', 'true');
        nav.classList.add('is-open');
    }

    btn.addEventListener('click', () => {
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        expanded ? closeMenu() : openMenu();
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 1050) closeMenu();
    });
}
