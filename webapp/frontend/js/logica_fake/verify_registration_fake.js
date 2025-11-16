/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Lógica fake para verify-registration. Solo llama a la API.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class VerifyFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async verificar(correo, verification_code) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/verify-registration', {
            correo, verification_code
        });
    }

    async reenviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/resend-verification', { correo });
    }
}
