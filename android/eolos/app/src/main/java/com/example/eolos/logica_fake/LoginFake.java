/**
 * Fichero: LoginFake.java
 * Descripción: Clase que envía peticiones REST para login.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 27/10/2025
 */

package com.example.eolos.logica_fake;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class LoginFake {

    private static final String BASE_URL = "http://172.20.10.12:8000";
    private static final String ENDPOINT_LOGIN = "/api/v1/auth/login";

    public interface LoginCallback {
        void onSuccess(String token);
        void onError(String error);
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Realiza el login enviando correo y contraseña al endpoint de autenticación.
     *
     * @param correo     Correo electrónico del usuario
     * @param contrasena Contraseña en texto plano
     * @param callback   Callback con el token JWT o mensaje de error
     */
    public void login(String correo, String contrasena, LoginCallback callback) {
        PeticionarioREST peticionario = new PeticionarioREST();
        String url = BASE_URL + ENDPOINT_LOGIN;

        try {
            JSONObject body = new JSONObject();
            body.put("correo", correo);
            body.put("contrasena", contrasena);

            peticionario.hacerPeticionREST("POST", url, body.toString(), new PeticionarioREST.RespuestaREST() {
                @Override
                public void callback(int codigo, String cuerpo) {
                    if (codigo == 200) {
                        try {
                            JSONObject response = new JSONObject(cuerpo);
                            String token = response.getString("token");
                            callback.onSuccess(token);
                        } catch (Exception e) {
                            callback.onError("Error procesando respuesta: " + e.getMessage());
                        }
                    } else {
                        try {
                            JSONObject errorResponse = new JSONObject(cuerpo);
                            callback.onError(errorResponse.getString("detail"));
                        } catch (Exception e) {
                            callback.onError("Error: Código " + codigo);
                        }
                    }
                }
            });
        } catch (Exception e) {
            callback.onError("Error preparando petición: " + e.getMessage());
        }
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------