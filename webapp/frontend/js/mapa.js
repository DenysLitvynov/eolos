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

    // Sidebar Toggle (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });


});
