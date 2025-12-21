
export function cargarEstacionesBicicletas(map) {
    // Usamos la URL relativa a nuestro propio backend, que actúa como proxy
    // Asumimos que el backend corre en el mismo host/puerto o está configurado el proxy
    // Si estamos en desarrollo local, la URL completa podría ser necesaria si no hay proxy configurado en vite/nginx
    // Pero dado que el usuario pidió "siguiendo la estructura actual", usaremos la ruta relativa a la API del backend.

    // NOTA: Ajustar la URL base si es necesario. En el frontend actual parece que no hay una variable global para la API URL.
    // Usaremos una ruta relativa asumiendo que el frontend se sirve desde el mismo origen o hay un proxy.
    // Si falla, probaremos con localhost:8000 explícitamente.

    const apiUrl = "http://localhost:8000/api/v1/bicicletas/estaciones";

    fetch(apiUrl)
        .then(r => r.json())
        .then(estaciones => {
            estaciones.forEach(e => {
                if (!e.lat || !e.lon) return;

                const popup = `
                    <div style="min-width: 150px;">
                        <strong>🚲 ${e.name}</strong><br>
                        <hr style="margin: 5px 0;">
                        Bicis disponibles: <b>${e.available_bikes}</b><br>
                        Huecos libres: <b>${e.available_stands}</b><br>
                        Total: ${e.total_stands}
                    </div>
                `;

                const customIcon = L.icon({
                    iconUrl: '../../images/icono-bici.png',
                    iconSize: [32, 32],      // ancho, alto en píxeles
                    iconAnchor: [16, 32],    // punto de anclaje (centro abajo)
                    popupAnchor: [0, -32]    // posición del popup respecto al icono
                });

                L.marker([e.lat, e.lon], { icon: customIcon })
                    .addTo(map)
                    .bindPopup(popup);

            });
        })
        .catch(err => console.error("Error cargando estaciones de bicicletas:", err));
}
