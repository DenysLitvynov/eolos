export function cargarEstacionesDesdeApi() {
    return fetch("https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estacions-contaminacio-atmosferiques-estaciones-contaminacion-atmosfericas/records?limit=50")
        .then(r => r.json())
        .then(data => {
            const layerGroup = L.layerGroup();
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

                const customIcon = L.icon({
                    iconUrl: '../../images/icono-tiempo.png',
                    iconSize: [32, 32],      // ancho, alto en píxeles
                    iconAnchor: [16, 32],    // punto de anclaje (centro abajo)
                    popupAnchor: [0, -32]    // posición del popup respecto al icono
                });

                L.marker([lat, lon], { icon: customIcon })
                    .bindPopup(popup)
                    .addTo(layerGroup);

            });
            return layerGroup;
        })
        .catch(err => {
            console.error("Error API estaciones:", err);
            return L.layerGroup();
        });
}
