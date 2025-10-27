/**
 * Fichero: RegistroFake.java
 * Descripción: Clase que envía peticiones REST para registro y realiza auto-login.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 27/10/2025
 */

package com.example.eolos.logica_fake;

import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;

public class RegistroFake {

    private static final String BASE_URL = "http://10.0.2.2:8000";
    private static final String ENDPOINT_REGISTRO = "/api/v1/auth/registro";

    public interface RegistroCallback {
        void onSuccess(String token);
        void onError(String error);
    }

    public void registro(String nombre, String apellido, String correo, String targetaId, String contrasena, String contrasenaRepite, RegistroCallback callback) {
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

            peticionario.hacerPeticionREST("POST", url, body.toString(), new PeticionarioREST.RespuestaREST() {
                @Override
                public void callback(int codigo, String cuerpo) {
                    if (codigo == 200) {
                        // Registro exitoso, realizar auto-login
                        LoginFake loginFake = new LoginFake();
                        loginFake.login(correo, contrasena, new LoginFake.LoginCallback() {
                            @Override
                            public void onSuccess(String token) {
                                callback.onSuccess(token);
                            }

                            @Override
                            public void onError(String error) {
                                callback.onError("Error en auto-login: " + error);
                            }
                        });
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