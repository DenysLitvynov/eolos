/* 
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Logica fake para registro.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class RegistroFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async registro(nombre, apellido, correo, targeta_id, contrasena, contrasena_repite) {
        const url = '/api/v1/auth/registro';
        const body = { nombre, apellido, correo, targeta_id, contrasena, contrasena_repite };
        return await this.peticionario.hacerPeticionRest('POST', url, body);
    }
}

// ----------------------------------------------------------
