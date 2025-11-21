/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Clase de lógica fake para hacer peticiones a la ruta de registro en la api 
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class RegistroFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }

// ----------------------------------------------------------
// Método que envía los datos de registro al backend y devuelve la respuesta como promesa.
//
// nombre : string
// apellido : string
// correo : string
// targeta_id : string
// contrasena : string
// contrasena_repite : string
// acepta_politica : boolean
// -> registro() -> Promise<json>
// ----------------------------------------------------------
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
