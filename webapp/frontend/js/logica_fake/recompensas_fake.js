/*
Autor: Ariel Bejaran
Fecha: 05-12-2025
Descripción: Cliente fake (proxy) para gestionar incidencias desde el frontend.
Se apoya en `PeticionarioREST` para comunicarse con la API backend.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class RecompensasFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async obtenerRecompensas() {
    try {
        const url = `/api/v1/recompensas/obtener_recompensas`; 
        return this.peticionario.hacerPeticionRest('GET', url);
    } catch (e) {
        console.error('Error al obtener recompensas:', e);
        throw e;
    }
}
}