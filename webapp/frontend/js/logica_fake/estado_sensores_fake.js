/* 
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Proxy fake para estado de sensores.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class EstadoSensoresFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    // ----------------------------------------------------------
    // Método que obtiene todas las bicicletas con su estado
    //
    // -> obtenerBicicletas() -> Promise<json[]>
    // ----------------------------------------------------------
    async obtenerBicicletas() {
        const url = `/api/v1/estado-sensores/bicicletas`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }

    // ----------------------------------------------------------
    // Método que obtiene todas las mediciones de una placa
    //
    // placa_id : string
    // fecha_inicio : string (ISO, opcional)
    // fecha_fin : string (ISO, opcional)
    // -> obtenerMediciones() -> Promise<json[]>
    // ----------------------------------------------------------
    async obtenerMediciones(placa_id, fecha_inicio = null, fecha_fin = null) {
        let url = `/api/v1/estado-sensores/mediciones/${placa_id}`;
        
        const params = new URLSearchParams();
        if (fecha_inicio) params.append('fecha_inicio', fecha_inicio);
        if (fecha_fin) params.append('fecha_fin', fecha_fin);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        return await this.peticionario.hacerPeticionRest('GET', url);
    }

    // ----------------------------------------------------------
    // Método que elimina una medición específica
    //
    // lectura_id : string
    // -> eliminarMedicion() -> Promise<json>
    // ----------------------------------------------------------
    async eliminarMedicion(lectura_id) {
        const url = `/api/v1/estado-sensores/mediciones/${lectura_id}`;
        return await this.peticionario.hacerPeticionRest('DELETE', url);
    }

    // ----------------------------------------------------------
    // Método que elimina todas las mediciones anómalas de una placa
    //
    // placa_id : string
    // -> eliminarMedicionesAnómalas() -> Promise<json>
    // ----------------------------------------------------------
    async eliminarMedicionesAnómalas(placa_id) {
        const url = `/api/v1/estado-sensores/mediciones-anomalas/${placa_id}`;
        return await this.peticionario.hacerPeticionRest('DELETE', url);
    }
}

// ----------------------------------------------------------