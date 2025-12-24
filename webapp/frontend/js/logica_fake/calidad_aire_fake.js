/* 
Autor: Víctor Morant
Fecha: 20-11-2025
Descripción: Proxy fake para calidad del aire.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

// ----------------------------------------------------------

export class CalidadAireFake {
    constructor() {
        this.peticionario = new PeticionarioREST();
    }
    
    // ----------------------------------------------------------
    // Método que obtiene el AQI más reciente para una placa
    //
    // placa_id : string
    // -> obtenerAQI() -> Promise<json>
    // ----------------------------------------------------------
    async obtenerAQI(placa_id) {
        const url = `/api/v1/calidad-aire/aqi/${placa_id}`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }

    async obtenerHistorico24h(placa_id) {
        const url = `/api/v1/calidad-aire/historico-24h/${placa_id}`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }

    // ----------------------------------------------------------
    // Método que obtiene TODAS las mediciones de una placa
    //
    // placa_id : string
    // -> obtenerMediciones() -> Promise<json[]>
    // ----------------------------------------------------------
    async obtenerMediciones(placa_id) {
        const url = `/api/v1/calidad-aire/mediciones/${placa_id}`;
        return await this.peticionario.hacerPeticionRest('GET', url);
    }

    // ----------------------------------------------------------
    // Método que obtiene el último trayecto completado del usuario
    //
    // token : string (Bearer token)
    // -> obtenerUltimoTrayecto() -> Promise<json>
    // ----------------------------------------------------------
    async obtenerUltimoTrayecto(token) {
        const url = `/api/v1/trayectos/usuario/ultimo`;
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        return await this.peticionario.hacerPeticionRest('GET', url, null, headers);
    }

    // ----------------------------------------------------------
    // Método que obtiene los últimos 10 trayectos completados del usuario
    //
    // token : string (Bearer token)
    // -> obtenerUltimos() -> Promise<json[]>
    // ----------------------------------------------------------
    async obtenerUltimosTrayectos(token) {
        const url = `/api/v1/trayectos/usuario/ultimos`;
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        return await this.peticionario.hacerPeticionRest('GET', url, null, headers);
    }

}

// ----------------------------------------------------------
