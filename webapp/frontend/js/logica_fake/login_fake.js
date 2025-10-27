/* 
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Proxy fake para login.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class LoginFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async login(correo, contrasena) {
        const url = '/api/v1/auth/login';
        const body = { correo, contrasena };
        return await this.peticionario.hacerPeticionRest('POST', url, body);
    }
}

// ----------------------------------------------------------
