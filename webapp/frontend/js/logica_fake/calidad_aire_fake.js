/* 
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Proxy fake para calidad del aire.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class CalidadAireFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    // ----------------------------------------------------------
    // Método que obtiene el AQI más reciente para una placa
    //
    // placa_id : string
    // -> obtenerAQI() -> Promise<json>
    // ----------------------------------------------------------
    async obtenerAQI(placa_id) {
        const url = `/api/v1/calidad-aire/aqi/${placa_id}`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}

// ----------------------------------------------------------