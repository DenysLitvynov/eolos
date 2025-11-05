package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Clase: PerfilFake (versión JWT)
 * Descripción:
 *  - Carga y guarda el perfil contra el backend real usando JWT (GET/PUT /api/v1/perfil).
 *  - Si falla la red o el token, rellena datos de ejemplo locales.
 */
public class PerfilFake {

    private static final String TAG = "PerfilFake";

    // 📌 Cambia BASE_URL si ejecutas en dispositivo físico (usa IP de tu PC).
    private static final String BASE_URL = "http://10.0.2.2:8000";
    private static final String ENDPOINT_PERFIL = "/api/v1/perfil";

    // Campos de datos
    private String nombre;
    private String apellido;      // opcional (no lo usas en UI, pero lo soporta backend)
    private String correo;
    private String tarjeta;
    private String contrasena;
    private String fechaRegistro;

    public interface InitCallback { void onListo(PerfilFake perfil, boolean desdeServidor); }
    public interface SaveCallback { void onResult(boolean exito, int codigo, String cuerpo); }

    private final Context context;

    // ===== Constructores =====
    /** Recomendado: pasar Context para poder leer token en SharedPreferences */
    public PerfilFake(Context context) {
        this.context = context.getApplicationContext();
    }

    /** Carga inicial (intenta servidor con JWT; si falla -> ejemplo local) */
    public PerfilFake(Context context, InitCallback cb) {
        this.context = context.getApplicationContext();
        inicializarPerfil(cb);
    }

    // ===== Carga de perfil desde backend con JWT =====
    public void inicializarPerfil(InitCallback cb) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        if (token == null || token.trim().isEmpty()) {
            Log.w(TAG, "Sin token, usando datos locales de ejemplo");
            cargarPerfilEjemplo();
            if (cb != null) cb.onListo(this, false);
            return;
        }

        String url = BASE_URL + ENDPOINT_PERFIL;
        Log.d(TAG, "➡️ GET " + url);

        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth("GET", url, null, token, (codigo, cuerpo) -> {
            Log.d(TAG, "GET resp code=" + codigo + ", body=" + cuerpo);

            if (codigo >= 200 && codigo < 300) {
                try {
                    if (fromJsonServidor(cuerpo)) {
                        if (cb != null) cb.onListo(this, true);
                        return;
                    }
                } catch (JSONException e) {
                    Log.e(TAG, "Error JSON: " + e.getMessage());
                }
            }

            Log.w(TAG, "Fallo GET perfil, usando ejemplo local");
            cargarPerfilEjemplo();
            if (cb != null) cb.onListo(this, false);
        });
    }

    // ===== Guardado en backend con JWT (PUT /perfil) =====
    public void guardarPerfil(SaveCallback cb) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        if (token == null || token.trim().isEmpty()) {
            if (cb != null) cb.onResult(false, 401, "Sin token JWT");
            return;
        }

        String url = BASE_URL + ENDPOINT_PERFIL;
        String cuerpoJson = toJsonServidor(); // mapea a los campos que espera tu backend

        Log.d(TAG, "➡️ PUT " + url);
        Log.d(TAG, "📦 body: " + cuerpoJson);

        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth("PUT", url, cuerpoJson, token, (codigo, cuerpo) -> {
            Log.d(TAG, "✅ PUT resp code=" + codigo + ", body=" + cuerpo);
            boolean exito = (codigo >= 200 && codigo < 300);
            if (exito) {
                try {
                    fromJsonServidor(cuerpo); // refrescar datos locales con lo devuelto
                } catch (JSONException ignored) {}
            }
            if (cb != null) cb.onResult(exito, codigo, cuerpo);
        });
    }

    // ===== JSON <-> Objeto (según tu backend JWT) =====
    private boolean fromJsonServidor(String cuerpo) throws JSONException {
        JSONObject o = new JSONObject(cuerpo);
        this.nombre = o.optString("nombre", "");
        this.apellido = o.optString("apellido", "");
        this.correo = o.optString("correo", "");
        this.tarjeta = o.optString("targeta_id", "");   // 🛈 en BD se llama targeta_id
        this.fechaRegistro = o.optString("fecha_registro", "");
        this.contrasena = ""; // nunca viene la contraseña en claro
        return (this.correo != null && !this.correo.isEmpty());
    }

    /** Cuerpo esperado por PUT /api/v1/perfil */
    private String toJsonServidor() {
        JSONObject o = new JSONObject();
        try {
            // Campos soportados por PerfilUpdateIn (backend):
            // nombre, apellido, correo, targeta_id, contrasena
            if (nombre != null)      o.put("nombre", nombre);
            if (apellido != null)    o.put("apellido", apellido);
            if (correo != null)      o.put("correo", correo);
            if (tarjeta != null)     o.put("targeta_id", tarjeta);
            if (contrasena != null && !contrasena.isEmpty()) {
                o.put("contrasena", contrasena); // el backend la encripta si viene
            } else {
                o.put("contrasena", JSONObject.NULL); // para "no cambiar" contraseña
            }
        } catch (JSONException ignored) {}
        return o.toString();
    }

    // ===== Datos de ejemplo (fallback local) =====
    private void cargarPerfilEjemplo() {
        this.nombre = "Ejemplo Usuario";
        this.apellido = "Demo";
        this.correo = "ejemplo@eolos.com";
        this.tarjeta = "ABC123";
        this.contrasena = "password";
        this.fechaRegistro = new SimpleDateFormat("d/M/yyyy", Locale.getDefault()).format(new Date());
    }

    // ===== Getters / Setters =====
    public String getNombre() { return nombre; }
    public String getApellido() { return apellido; }
    public String getCorreo() { return correo; }
    public String getTarjeta() { return tarjeta; }
    public String getContrasena() { return contrasena; }
    public String getFechaRegistro() { return fechaRegistro; }

    public void setNombre(String nombre) { this.nombre = nombre; }
    public void setApellido(String apellido) { this.apellido = apellido; }
    public void setCorreo(String correo) { this.correo = correo; }
    public void setTarjeta(String tarjeta) { this.tarjeta = tarjeta; }
    public void setContrasena(String contrasena) { this.contrasena = contrasena; }
    public void setFechaRegistro(String fechaRegistro) { this.fechaRegistro = fechaRegistro; }

    @Override
    public String toString() {
        return "PerfilFake{" +
                "nombre='" + nombre + '\'' +
                ", apellido='" + apellido + '\'' +
                ", correo='" + correo + '\'' +
                ", tarjeta='" + tarjeta + '\'' +
                ", contrasena='" + contrasena + '\'' +
                ", fechaRegistro='" + fechaRegistro + '\'' +
                '}';
    }
}
