/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Lógica fake para registro.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class RegistroFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async registro(nombre, apellido, correo, targeta_id, contrasena, contrasena_repite, acepta_politica) {
        const url = '/api/v1/auth/registro';
        const body = { 
            nombre, 
            apellido, 
            correo, 
            targeta_id, 
            contrasena, 
            contrasena_repite,
            acepta_politica  
        };
        console.log("ENVIANDO REGISTRO:", body); 
        return await this.peticionario.hacerPeticionRest('POST', url, body);
    }
}

// ----------------------------------------------------------
