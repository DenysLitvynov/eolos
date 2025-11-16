/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Lógica fake para reset-password. Solo llama a la API.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class ResetPasswordFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async resetear(token, contrasena, contrasena_repite) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/reset-password', {
            token, contrasena, contrasena_repite
        });
    }
}
