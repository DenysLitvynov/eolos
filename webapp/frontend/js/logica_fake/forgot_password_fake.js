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

    // ----------------------------------------------------------
    // Método que solicita el envío del enlace de recuperación al correo indicado.
    //
    // correo : string
    // -> enviar() -> Promise<json>
    // ----------------------------------------------------------
    async enviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/forgot-password', { correo });
    }

    // ----------------------------------------------------------
    // Método que reenvía el enlace de recuperación (genera uno nuevo).
    //
    // correo : string
    // -> reenviar() -> Promise<json>
    // ----------------------------------------------------------
    async reenviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/resend-reset', { correo });
    }
}
