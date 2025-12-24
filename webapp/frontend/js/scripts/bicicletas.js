import { BicicletasFake } from '../logica_fake/bicicletas_fake.js';

export function cargarEstacionesBicicletas() {
    const logica = new BicicletasFake();

    return logica.obtenerEstaciones()
        .then(estaciones => {
            const layerGroup = L.layerGroup();
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
                    .bindPopup(popup)
                    .addTo(layerGroup);
            });
            return layerGroup;
        })
        .catch(err => {
            console.error("Error cargando estaciones de bicicletas:", err);
            return L.layerGroup(); // Retorna grupo vacío en caso de error
        });
}
