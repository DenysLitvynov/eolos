/**
 * Fichero: RegistroFake.java
 * Descripción: Clase que envía petición REST para iniciar registro (sin auto-login).
 *              Solo envía el formulario y espera código de verificación.
 * @author Denys Litvynov Lymanets
 * @version 2.0
 * @since 16/11/2025
 */

package com.example.eolos.logica_fake;

import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class RegistroFake {

    private static final String BASE_URL = "http://10.0.2.2:8000";
    private static final String ENDPOINT_REGISTRO = "/api/v1/auth/registro";

    /**
     * Callback para el registro.
     * - onCodigoEnviado(): el backend aceptó el registro y envió el código al correo
     * - onError(): error en validación, conexión, etc.
     */
    public interface RegistroCallback {
        void onCodigoEnviado();
        void onError(String error);
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Inicia el proceso de registro enviando todos los datos del formulario al backend.
     *
     * @param nombre            Nombre del usuario
     * @param apellido          Apellido del usuario
     * @param correo            Correo electrónico
     * @param targetaId         ID del carnet (DNI/NIE)
     * @param contrasena        Contraseña
     * @param contrasenaRepite  Repetición de contraseña
     * @param aceptaPolitica    Aceptación de política de privacidad
     * @param callback          Callback con resultado
     */
    public void registro(String nombre, String apellido, String correo, String targetaId,
                         String contrasena, String contrasenaRepite, boolean aceptaPolitica,
                         RegistroCallback callback) {

        PeticionarioREST peticionario = new PeticionarioREST();
        String url = BASE_URL + ENDPOINT_REGISTRO;

        try {
            JSONObject body = new JSONObject();
            body.put("nombre", nombre);
            body.put("apellido", apellido);
            body.put("correo", correo);
            body.put("targeta_id", targetaId);
            body.put("contrasena", contrasena);
            body.put("contrasena_repite", contrasenaRepite);
            body.put("acepta_politica", aceptaPolitica); // ← campo obligatorio

            Log.d("RegistroFake", "Enviando registro: " + body.toString());

            peticionario.hacerPeticionREST("POST", url, body.toString(), new PeticionarioREST.RespuestaREST() {
                @Override
                public void callback(int codigo, String cuerpo) {
                    Log.d("RegistroFake", "Respuesta del servidor: código=" + codigo + ", cuerpo=" + cuerpo);

                    if (codigo == 200) {
                        Log.d("RegistroFake", "ÉXITO: Código enviado → llamando onCodigoEnviado()");
                        callback.onCodigoEnviado();
                    } else {
                        try {
                            JSONObject errorResponse = new JSONObject(cuerpo);
                            String mensaje = errorResponse.getString("detail");
                            Log.e("RegistroFake", "Error backend: " + mensaje);
                            callback.onError(mensaje);
                        } catch (Exception e) {
                            Log.e("RegistroFake", "Error parseando error", e);
                            callback.onError("Error: " + codigo);
                        }
                    }
                }
            });

        } catch (Exception e) {
            Log.e("RegistroFake", "Error preparando petición", e);
            callback.onError("Error de conexión: " + e.getMessage());
        }
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------