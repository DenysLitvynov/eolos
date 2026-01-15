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
async obtenerRecompensasUsuario() {
    try {
        const url = `/api/v1/recompensas/recompensas_obtenidas`;
        // Recuperamos el token que guardaste al hacer login
        const token = localStorage.getItem('token'); 

        return await this.peticionario.hacerPeticionRest('GET', url, null, {
            'Authorization': `Bearer ${token}` 
        });
    } catch (e) {
        console.error('Error:', e);
        throw e;
    }
}

async obtenerDistanciaRecorrida() {
    try {
        const url = `/api/v1/recompensas/obtener_distancia_acumulada`;
        const token = localStorage.getItem('token'); 

        const data = await this.peticionario.hacerPeticionRest('GET', url, null, {
            'Authorization': `Bearer ${token}` // <--- Faltaba esto
        });
        return data.km_acumulados; 
    } catch (e) {
        console.error("Error al obtener distancia:", e);
        return 0; 
    }
}

}