export function cargarEstacionesDesdeApi(map) {
    fetch("https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estacions-contaminacio-atmosferiques-estaciones-contaminacion-atmosfericas/records?limit=50")
        .then(r => r.json())
        .then(data => {
            data.results.forEach(e => {
                if (!e.geo_point_2d) return;

                const lat = e.geo_point_2d.lat;
                const lon = e.geo_point_2d.lon;

                const popup = `
                    <strong>${e.nombre}</strong><br>
                    NO₂: ${e.no2 ?? "-"}<br>
                    O₃: ${e.o3 ?? "-"}<br>
                    PM10: ${e.pm10 ?? "-"}<br>
                    PM2.5: ${e.pm25 ?? "-"}<br>
                    Calidad: ${e.calidad_am}
                `;

                L.marker([lat, lon])
                    .addTo(map)
                    .bindPopup(popup);
            });
        })
        .catch(err => console.error("Error API estaciones:", err));
}
