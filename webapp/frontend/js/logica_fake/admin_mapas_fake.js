// File: frontend/js/logica_fake/admin_mapas_fake.js
/**
 * Autor: Denys Litvynov Lymanets
 * Fecha: 05-12-2025
 * Descripción: Clase fake para peticiones API de admin mapas.
 */

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class AdminMapasFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    // ----------------------------------------------------------
    // Método para obtener mapa admin con params históricos.
    //
    // tipo : string
    // dia : string (YYYY-MM-DD)
    // lat_min : number
    // lon_min : number
    // lat_max : number
    // lon_max : number
    // -> obtenerMapaAdmin() -> Promise<json>
    // ----------------------------------------------------------
    async obtenerMapaAdmin(tipo, dia, lat_min, lon_min, lat_max, lon_max) {
        if (!dia || isNaN(lat_min) || isNaN(lon_min) || isNaN(lat_max) || isNaN(lon_max)) {
            throw new Error("Parámetros inválidos para admin mapas");
        }

        const url = `/api/v1/admin-mapas/obtener-mapa-admin?` + new URLSearchParams({
            tipo: tipo,
            dia: dia,
            lat_min: lat_min.toFixed(6),
            lon_min: lon_min.toFixed(6),
            lat_max: lat_max.toFixed(6),
            lon_max: lon_max.toFixed(6)
        }).toString();

        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}
