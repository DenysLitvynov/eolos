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

// Obtiene las incidencias filtradas según el rol del usuario autenticado
    async obtenerIncidenciasFiltradas() {
        const url = `/api/v1/gestion-incidencias/admin_tecnico`;
        // Nota: la ruta de cambio de estado se construye con query params en `cambiarEstadoIncidencia`.

     // Centralizamos la lógica en la petición autenticada,
        // ya que la ruta '/filtradas' REQUIERE token.
        
     try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            
            if (!token) {
                // Si no hay token, el usuario no está autenticado para esta página.
                console.error("No se encontró token de autenticación. Acceso denegado a /filtradas.");
                throw new Error("Usuario no autenticado.");
            }
            
            // Realizar la petición con el token JWT
        const resp = await fetch(url, {
                method: 'GET',
                headers: { 
                    'Content-Type': 'application/json', 
                    'Authorization': `Bearer ${token}` 
                }
            });
            
        if (!resp.ok) {
         const text = await resp.text();
                // 401/403 (No autorizado/Prohibido) o 500 (Error del servidor)
            throw new Error(`Error ${resp.status}: Fallo al obtener incidencias filtradas. ${text}`);
            }
            
             return await resp.json();
            
             } catch (e) {
         // Manejo de errores de red, token faltante o errores HTTP
         console.error('Petición a incidencias filtradas fallida:', e);
            // Propagamos el error para que la página de gestión de incidencias lo maneje
         throw e; 
        }

 // Eliminamos la llamada a this.peticionario.hacerPeticionRest 
        // porque la ruta /filtradas siempre debe ir con token.
    }

    async cambiarEstadoIncidencia(idIncidencia, nuevoEstado) {
        // FastAPI espera parámetros query para `incidencia_id` y `nuevo_estado`.
        const url = `/api/v1/gestion-incidencias/cambiar_estado?incidencia_id=${encodeURIComponent(idIncidencia)}&nuevo_estado=${encodeURIComponent(nuevoEstado)}`;
        // Usamos fetch directo para adjuntar Authorization (no tocar `peticionario_REST.js`)
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            if (!token) {
                throw new Error('Usuario no autenticado. Falta token.');
            }

            const resp = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!resp.ok) {
                const text = await resp.text();
                throw new Error(`Error ${resp.status}: ${text}`);
            }

            return await resp.json();
        } catch (e) {
            console.error('Error en cambiarEstadoIncidencia:', e);
            throw e;
        }
    }

}