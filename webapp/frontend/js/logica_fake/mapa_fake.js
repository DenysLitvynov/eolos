// File: frontend/js/logica_fake/mapa_fake.js (CORREGIDO)

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class MapaFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    async obtenerMapa(tipo, dia, lat_min, lon_min, lat_max, lon_max) {
        // Asegúrate de que todos los valores son números válidos
        if (!dia || isNaN(lat_min) || isNaN(lon_min) || isNaN(lat_max) || isNaN(lon_max)) {
            throw new Error("Parámetros de bounds inválidos");
        }

        const url = `/api/v1/mapas/obtener-mapa?` + new URLSearchParams({
            tipo: tipo,
            dia: dia,
            lat_min: lat_min.toFixed(6),
            lon_min: lon_min.toFixed(6),
            lat_max: lat_max.toFixed(6),
            lon_max: lon_max.toFixed(6)
        }).toString();

        console.log("Llamando a:", url); // <-- Esto te ayudará a depurar

        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}
