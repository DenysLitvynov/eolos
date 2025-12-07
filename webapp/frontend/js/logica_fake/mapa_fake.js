/**
 * Autor: Denys Litvynov Lymanets
 * Fecha: 05-12-2025
 * Descripción: Clase proxy para peticiones API de mapas públicos (no admin).
 */

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class MapaFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    // ----------------------------------------------------------
    // Método para obtener el mapa público con parámetros históricos.
    //
    // tipo      : string  (ej: "pm2_5", "general", etc.)
    // dia       : string  (formato YYYY-MM-DD)
    // lat_min   : number
    // lon_min   : number
    // lat_max   : number
    // lon_max   : number
    // -> obtenerMapa() -> Promise<json>
    // ----------------------------------------------------------
    async obtenerMapa(tipo, dia, lat_min, lon_min, lat_max, lon_max) {
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

        console.log("Llamando a:", url);

        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}
