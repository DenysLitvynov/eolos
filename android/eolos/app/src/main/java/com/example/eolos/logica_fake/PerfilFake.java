package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * PerfilFake (versión final sin fecha)
 *
 * Gestiona:
 *  - GET perfil (nombre, correo, targeta_id)
 *  - PUT perfil (cambiar datos + contraseña actual + nueva contraseña opcional)
 *
 * Payload esperado por backend (igual que frontend perfil.js):
 *
 * {
 *   "nombre": string | null,
 *   "apellido": null,
 *   "correo": string | null,
 *   "targeta_id": string | null,
 *   "contrasena_actual": string,      // siempre obligatoria
 *   "contrasena_nueva": string | null // opcional
 * }
 */
public class PerfilFake {

    private static final String TAG = "PerfilFake";

    private static final String BASE_URL = "http://172.20.10.12:8000";
    private static final String ENDPOINT_PERFIL = "/api/v1/perfil";

    // ==== Datos del perfil ====
    private String nombre;
    private String correo;
    private String tarjeta; // targeta_id en BD

    // ==== Password para actualización ====
    private String contrasenaActual;
    private String contrasenaNueva;

    public interface InitCallback { void onListo(PerfilFake perfil, boolean desdeServidor); }
    public interface SaveCallback { void onResult(boolean exito, int codigo, String cuerpo); }

    private final Context context;

    public PerfilFake(Context context) {
        this.context = context.getApplicationContext();
    }

    public PerfilFake(Context context, InitCallback cb) {
        this.context = context.getApplicationContext();
        inicializarPerfil(cb);
    }

    // ====================================================================
    // 🔹 Cargar perfil desde backend con JWT
    // ====================================================================
    public void inicializarPerfil(InitCallback cb) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        if (token == null || token.trim().isEmpty()) {
            Log.w(TAG, "Sin token → usando ejemplo local");
            cargarPerfilEjemplo();
            if (cb != null) cb.onListo(this, false);
            return;
        }

        String url = BASE_URL + ENDPOINT_PERFIL;
        Log.d(TAG, "➡️ GET " + url);

        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth("GET", url, null, token, (codigo, cuerpo) -> {
            Log.d(TAG, "GET resp = " + codigo + ", body=" + cuerpo);

            if (codigo >= 200 && codigo < 300) {
                try {
                    if (fromJsonServidor(cuerpo)) {
                        guardarTargetaIdEnPrefs();
                        if (cb != null) cb.onListo(this, true);
                        return;
                    }
                } catch (JSONException e) {
                    Log.e(TAG, "Error JSON: " + e.getMessage());
                }
            }

            Log.w(TAG, "GET perfil falló → ejemplo local");
            cargarPerfilEjemplo();
            guardarTargetaIdEnPrefs();
            if (cb != null) cb.onListo(this, false);
        });
    }

    // ====================================================================
    // 🔹 Guardar targeta_id en SharedPreferences
    // ====================================================================
    private void guardarTargetaIdEnPrefs() {
        if (tarjeta != null && !tarjeta.trim().isEmpty()) {
            SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
            prefs.edit().putString("targeta_id", tarjeta.trim()).apply();
            Log.d(TAG, "targeta_id guardada en prefs: " + tarjeta);
        }
    }

    // ====================================================================
    // 🔹 Guardar perfil en backend (PUT /perfil)
    // ====================================================================
    public void guardarPerfil(SaveCallback cb) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        if (token == null || token.trim().isEmpty()) {
            if (cb != null) cb.onResult(false, 401, "Sin token JWT");
            return;
        }

        String url = BASE_URL + ENDPOINT_PERFIL;
        String cuerpoJson = toJsonServidor();

        Log.d(TAG, "➡️ PUT " + url);
        Log.d(TAG, "📦 JSON enviado = " + cuerpoJson);

        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth("PUT", url, cuerpoJson, token, (codigo, cuerpo) -> {
            Log.d(TAG, "PUT resp = " + codigo + ", body=" + cuerpo);

            boolean exito = (codigo >= 200 && codigo < 300);
            if (exito) {
                try {
                    fromJsonServidor(cuerpo);
                    guardarTargetaIdEnPrefs();
                } catch (JSONException ignored) {}
            }

            if (cb != null) cb.onResult(exito, codigo, cuerpo);
        });
    }

    // ====================================================================
    // 🔹 JSON → objeto local
    // ====================================================================
    private boolean fromJsonServidor(String cuerpo) throws JSONException {
        JSONObject o = new JSONObject(cuerpo);

        this.nombre  = o.optString("nombre", "");
        this.correo  = o.optString("correo", "");
        this.tarjeta = o.optString("targeta_id", "");

        // nunca guardamos contraseñas
        this.contrasenaActual = null;
        this.contrasenaNueva  = null;

        return (this.correo != null && !this.correo.isEmpty());
    }

    // ====================================================================
    // 🔹 Construir JSON para PUT /perfil
    // ====================================================================
    private String toJsonServidor() {
        JSONObject o = new JSONObject();
        try {
            o.put("nombre", nombre == null ? JSONObject.NULL : nombre);
            o.put("apellido", JSONObject.NULL); // igual que frontend
            o.put("correo", correo == null ? JSONObject.NULL : correo);

            if (tarjeta == null || tarjeta.trim().isEmpty()) {
                o.put("targeta_id", JSONObject.NULL);
            } else {
                o.put("targeta_id", tarjeta.trim());
            }

            // contraseña actual (obligatoria)
            o.put("contrasena_actual",
                    (contrasenaActual == null || contrasenaActual.trim().isEmpty())
                            ? JSONObject.NULL
                            : contrasenaActual.trim());

            // nueva contraseña (opcional)
            o.put("contrasena_nueva",
                    (contrasenaNueva == null || contrasenaNueva.trim().isEmpty())
                            ? JSONObject.NULL
                            : contrasenaNueva.trim());

        } catch (JSONException ignored) {}

        return o.toString();
    }

    // ====================================================================
    // 🔹 Ejemplo local sin fecha
    // ====================================================================
    private void cargarPerfilEjemplo() {
        this.nombre  = "Ejemplo Usuario";
        this.correo  = "ejemplo@eolos.com";
        this.tarjeta = "USER_001";
    }

    // ====================================================================
    // 🔹 GETTERS / SETTERS
    // ====================================================================
    public String getNombre() { return nombre; }
    public String getCorreo() { return correo; }
    public String getTarjeta() { return tarjeta; }

    public void setNombre(String nombre) { this.nombre = nombre; }
    public void setCorreo(String correo) { this.correo = correo; }
    public void setTarjeta(String tarjeta) { this.tarjeta = tarjeta; }

    // Nuevos campos de contraseña usados por PerfilActivity
    public String getContrasenaActual() { return contrasenaActual; }
    public void setContrasenaActual(String contrasenaActual) { this.contrasenaActual = contrasenaActual; }

    public String getContrasenaNueva() { return contrasenaNueva; }
    public void setContrasenaNueva(String contrasenaNueva) { this.contrasenaNueva = contrasenaNueva; }

    @Override
    public String toString() {
        return "PerfilFake{" +
                "nombre='" + nombre + '\'' +
                ", correo='" + correo + '\'' +
                ", tarjeta='" + tarjeta + '\'' +
                '}';
    }
}
