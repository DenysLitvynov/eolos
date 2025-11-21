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

    // ----------------------------------------------------------
    // Método que envía el token recibido por email y las nuevas contraseñas al backend.
    //
    // token : string
    // contrasena : string
    // contrasena_repite : string
    // -> resetear() -> Promise<json>
    // ----------------------------------------------------------
    async resetear(token, contrasena, contrasena_repite) {
        return await this.peticionario.hacerPeticionRest('POST', '/api/v1/auth/reset-password', {
            token, contrasena, contrasena_repite
        });
    }
}
