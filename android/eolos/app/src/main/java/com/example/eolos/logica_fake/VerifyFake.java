/**
 * Fichero: VerifyFake.java
 * Descripción: Clase que envía petición REST para verificar el correo del usuario.
 * @author Denys Litvynov Lymanets
 * @version 2.0
 * @since 16/11/2025
 */

package com.example.eolos.logica_fake;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class VerifyFake {

    private static final String BASE_URL = "http://192.168.1.133:8000";

    public interface VerifyCallback {
        void onSuccess(String token);
        void onError(String error);
    }

    public interface ReenvioCallback {
        void onReenviado();
        void onError(String error);
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Envía el código de verificación al backend para completar el registro.
     *
     * @param correo            Correo electrónico del usuario
     * @param verification_code Código de 6 dígitos recibido por email
     * @param callback          Callback que recibe el token JWT o error
     */
    public void verificar(String correo, String verification_code, VerifyCallback callback) {
        PeticionarioREST p = new PeticionarioREST();
        String url = BASE_URL + "/api/v1/auth/verify-registration";

        try {
            JSONObject body = new JSONObject();
            body.put("correo", correo);
            body.put("verification_code", verification_code);

            p.hacerPeticionREST("POST", url, body.toString(), (codigo, cuerpo) -> {
                if (codigo == 200) {
                    try {
                        JSONObject resp = new JSONObject(cuerpo);
                        String token = resp.getString("token");
                        callback.onSuccess(token);
                    } catch (Exception e) {
                        callback.onError("Error procesando respuesta");
                    }
                } else {
                    try {
                        JSONObject err = new JSONObject(cuerpo);
                        callback.onError(err.getString("detail"));
                    } catch (Exception e) {
                        callback.onError("Error en verificación");
                    }
                }
            });
        } catch (Exception e) {
            callback.onError(e.getMessage());
        }
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Solicita el reenvío del código de verificación al correo indicado.
     *
     * @param correo    Correo electrónico del usuario pendiente de verificación
     * @param callback  Callback que notifica éxito o error
     */
    public void reenviar(String correo, ReenvioCallback callback) {
        PeticionarioREST p = new PeticionarioREST();
        String url = BASE_URL + "/api/v1/auth/resend-verification";

        try {
            JSONObject body = new JSONObject();
            body.put("correo", correo);
            p.hacerPeticionREST("POST", url, body.toString(), (codigo, cuerpo) -> {
                if (codigo == 200) {
                    callback.onReenviado();
                } else {
                    try {
                        JSONObject err = new JSONObject(cuerpo);
                        callback.onError(err.getString("detail"));
                    } catch (Exception e) {
                        callback.onError("Error");
                    }
                }
            });
        } catch (Exception e) {
            callback.onError(e.getMessage());
        }
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------