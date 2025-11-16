package com.example.eolos.logica_fake;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;

public class VerifyFake {

    private static final String BASE_URL = "http://10.0.2.2:8000";

    public interface VerifyCallback {
        void onSuccess(String token);
        void onError(String error);
    }

    public interface ReenvioCallback {
        void onReenviado();
        void onError(String error);
    }

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