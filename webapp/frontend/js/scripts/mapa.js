document.addEventListener('DOMContentLoaded', () => {
    // Inicializar mapa
    const map = L.map('map', {
        zoomControl: false
    }).setView([39.4699, -0.3763], 13); // Centrado en Valencia

    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Date Filter Listener
    const dateFilter = document.getElementById('date-filter');
    if (dateFilter) {
        // Set default to today
        const today = new Date().toISOString().split('T')[0];
        dateFilter.value = today;

        dateFilter.addEventListener('change', (e) => {
            const selectedDate = e.target.value;
            console.log(`Fecha seleccionada: ${selectedDate}`);
            updateMapFilters();
        });
    }

    // Function stubs for map interactions
    function loadMapData() {
        console.log('Loading map data...');
    }

    function updateMapFilters() {
        console.log('Updating map filters...');
    }

    function handleLayerToggle(layerId, isVisible) {
        console.log(`Toggling layer ${layerId}: ${isVisible}`);
    }

    // Initial data load
    loadMapData();

    // Sidebar Toggle (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });


});



const header = document.querySelector('.header');
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
