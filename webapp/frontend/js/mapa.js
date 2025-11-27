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
            // Aquí iría la lógica para filtrar los datos del mapa según la fecha
        });
    }

    // Time Filter Listener
    const timeFilter = document.getElementById('time-filter');
    if (timeFilter) {
        // Set default to current time
        const now = new Date();
        const currentTime = now.toTimeString().slice(0, 5); // Format HH:MM
        timeFilter.value = currentTime;

        timeFilter.addEventListener('change', (e) => {
            const selectedTime = e.target.value;
            console.log(`Hora seleccionada: ${selectedTime}`);
            // Aquí iría la lógica para filtrar los datos del mapa según la hora
        });
    }

    // Sidebar Toggle (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });


});
