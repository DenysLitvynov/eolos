/**
 * Fichero: LogicaFake.java
 * Descripción: Lógica fake para enviar medidas al servidor REST.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 25/09/2025
 */

package com.example.eolos.logica_fake;

import android.util.Log;

import com.example.eolos.PeticionarioREST;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class LogicaFake {

    public LogicaFake() {
        super(); // llama al constructor de Object
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Envía una medida en formato JSON a un servidor REST específico.
     *
     * Construye la URL completa combinando la base del servidor y el endpoint,
     * luego realiza una petición HTTP POST asíncrona y maneja la respuesta mediante callback.
     *
     * @param jsonMedida String con los datos de la medida en formato JSON
     * @param baseUrl String con la URL base del servidor (ej. "http://192.168.1.100:8000")
     * @param endpoint String con el endpoint de la API (ej. "/api/v1/guardar-medida")
     * @return void
     */

    public void guardarMedida(String jsonMedida, String baseUrl, String endpoint) {
        String urlCompleta = baseUrl + endpoint;  // <- Construye la URL full aquí (ej. "http://192.168.1.100:8000" + "/api/v1/guardar-medida")
        Log.d("LogicaFake", "URL construida: " + urlCompleta);  // Para depurar

        PeticionarioREST elPeticionario = new PeticionarioREST();

        elPeticionario.hacerPeticionREST("POST", urlCompleta, jsonMedida,
                new PeticionarioREST.RespuestaREST() {
                    @Override
                    public void callback(int codigo, String cuerpo) {
                        Log.d("LogicaFake", "Respuesta del servidor: codigo=" + codigo + ", cuerpo=" + cuerpo);
                    }
                });
    }

} // class

// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------