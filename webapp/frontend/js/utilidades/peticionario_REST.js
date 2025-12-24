/* 
Autor: Denys Litvynov Lymanets
Fecha: 29-09-2025
Descripción: Módulo encargado de realizar peticiones REST al backend. Contiene funciones de GET, POST, PUT y DELETE.
*/

// ----------------------------------------------------------

export class PeticionarioREST {

    // ----------------------------------------------------------
    // Método que realiza peticiones HTTP a la API y devuelve la respuesta en JSON como promesa.  
    //
    // method : string
    // url    : string
    // body   : json | null
    // headers : object | null (headers adicionales)
    // -> hacerPeticionRest() -> Promise<json>
    // ----------------------------------------------------------
    async hacerPeticionRest(method, url, body = null, headers = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type' : 'application/json',
                ...(headers || {})
            }
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        return await response.json();
    }
}

// ----------------------------------------------------------
