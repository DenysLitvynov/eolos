document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([39.4699, -0.3763], 12);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    function colorPorAQI(aqi) {
        if (aqi <= 50) return '#00e400';   // Buena
        if (aqi <= 100) return '#ffff00';  // Moderada
        if (aqi <= 150) return '#ff7e00';  // Mala
        if (aqi <= 200) return '#ff0000';  // Muy mala
        return '#7e0023';                  // Peligrosa
    }

    fetch('/calidad-aire/mapa')  // 就是刚才新加的接口
        .then(r => r.json())
        .then(puntos => {
            puntos.forEach(p => {
                const color = colorPorAQI(p.aqi);
                L.circleMarker([p.lat, p.lon], {
                    radius: 10,
                    color,
                    fillColor: color,
                    fillOpacity: 0.8
                })
                    .bindPopup(
                        `<b>Placa:</b> ${p.placa_id}<br>` +
                        `<b>AQI:</b> ${p.aqi}<br>` +
                        `<b>Fecha:</b> ${p.fecha_hora}`
                    )
                    .addTo(map);
            });
        });
});
