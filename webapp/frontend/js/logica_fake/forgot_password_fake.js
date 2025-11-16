/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Lógica fake para forgot-password. Solo llama a la API.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class ForgotPasswordFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

    async enviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/forgot-password', { correo });
    }

    async reenviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/resend-reset', { correo });
    }
}
