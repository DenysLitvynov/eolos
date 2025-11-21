/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Logica fake para hacer peticiones a la API para la verificación de contraseña. 
*/

// ----------------------------------------------------------

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

export class VerifyFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

// ----------------------------------------------------------
// Método que envía el correo y código para verificar el registro y devuelve la respuesta como promesa.
//
// correo : string
// verification_code : string
// -> verificar() -> Promise<json>
// ----------------------------------------------------------
    async verificar(correo, verification_code) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/verify-registration', {
            correo, verification_code
        });
    }

// ----------------------------------------------------------
// Método que envía el correo para reenviar el código de verificación y devuelve la respuesta como promesa.
//
// correo : string
// -> reenviar() -> Promise<json>
// ----------------------------------------------------------
    async reenviar(correo) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/resend-verification', { correo });
    }
}

// ----------------------------------------------------------
