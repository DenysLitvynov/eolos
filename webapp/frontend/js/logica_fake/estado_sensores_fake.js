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
}

// ----------------------------------------------------------