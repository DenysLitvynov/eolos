/*
Autor: Ariel Bejaran
Fecha: 05-12-2025
Descripción: Cliente fake (proxy) para gestionar incidencias desde el frontend.
Se apoya en `PeticionarioREST` para comunicarse con la API backend.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class GestionIncidenciasFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    // Obtiene las incidencias del usuario autenticado
    async obtenerMisIncidencias() {
        const url = `/api/v1/gestion-incidencias/public`;
        // Si existe un token JWT en localStorage lo usamos en la petición
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            if (token) {
                const resp = await fetch(url, {headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }});
                if (!resp.ok) {
                    const text = await resp.text();
                    throw new Error(`Error ${resp.status}: ${text}`);
                }
                return await resp.json();
            }
        } catch (e) {
            // si algo falla, caemos al peticionario REST normal
            console.warn('Petición con token fallida, usando PeticionarioREST:', e);
        }

        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}
