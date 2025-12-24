/* 
Autor: Hugo Belda Revert
Fecha: 24-12-2025
Descripción: Proxy fake para estaciones de bicicletas.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class BicicletasFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    // ----------------------------------------------------------
    // Método que obtiene todas las estaciones de bicicletas
    //
    // -> obtenerEstaciones() -> Promise<json[]>
    // ----------------------------------------------------------
    async obtenerEstaciones() {
        const url = `/api/v1/bicicletas/estaciones`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }
}
