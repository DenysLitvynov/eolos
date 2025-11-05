package com.example.eolos.logica_fake;

import android.util.Log;
import com.example.eolos.PeticionarioREST;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class PerfilFake {

    // ===================== Configuración de red =====================
    private static final String BASE_URL = "http://10.0.2.2:8000";               // Servidor local (en producción usar https://api.miapp.com)
    private static final String ENDPOINT_PERFIL = "/api/v1/perfil_api";          // Endpoint del perfil

    private static final String TAG = "PerfilFake";

    // ===================== Campos de datos =====================
    private String nombre;
    private String correo;
    private String tarjeta;
    private String contrasena;
    private String fechaRegistro;

    // ===================== Callback de inicialización =====================
    /**
     * Callback de inicialización:
     * desdeServidor = true  → datos obtenidos del servidor correctamente.
     * desdeServidor = false → se usaron datos de ejemplo locales.
     */
    public interface InitCallback {
        void onListo(PerfilFake perfil, boolean desdeServidor);
    }

    // ===================== Constructores =====================
    /**
     * Constructor por defecto: intenta primero obtener datos del servidor
     * (si previamente se ha establecido el correo).
     * Si no hay correo, carga directamente los datos de ejemplo.
     */
    public PerfilFake() {
        inicializarPerfil(null);
    }

    /**
     * Constructor recomendado: recibe un correo y un callback.
     * Intenta obtener el perfil desde el servidor según el correo.
     * Si no existe o falla, carga el ejemplo local.
     */
    public PerfilFake(String correoInicial, InitCallback cb) {
        this.correo = correoInicial;
        inicializarPerfil(cb);
    }

    // ===================== Lógica de inicialización =====================
    /**
     * Intenta obtener el perfil desde el servidor.
     * Si no hay datos o la petición falla, se cargan datos de ejemplo.
     *
     * Reglas:
     *  - Si hay correo → hace GET /perfil?correo=xxx
     *  - Si no hay correo → carga directamente el ejemplo
     */
    public void inicializarPerfil(InitCallback cb) {
        if (correo == null || correo.trim().isEmpty()) {
            Log.d(TAG, "Inicialización: sin correo, cargando ejemplo local");
            cargarPerfilEjemplo();
            if (cb != null) cb.onListo(this, false);
            return;
        }

        String encoded = correo;
        try { encoded = URLEncoder.encode(correo, "UTF-8"); } catch (UnsupportedEncodingException ignored) {}

        String url = BASE_URL + ENDPOINT_PERFIL + "?correo=" + encoded;
        Log.d(TAG, "Inicialización: intentando obtener perfil del servidor -> " + url);

        PeticionarioREST peticion = new PeticionarioREST();
        peticion.hacerPeticionREST("GET", url, null, (codigo, cuerpo) -> {
            Log.d(TAG, "GET resp code=" + codigo + ", body=" + cuerpo);

            boolean ok = false;
            if (codigo >= 200 && codigo < 300 && cuerpo != null && !cuerpo.trim().isEmpty() && !"null".equalsIgnoreCase(cuerpo.trim())) {
                try {
                    if (fromJsonSeguro(cuerpo)) {
                        ok = true; // Datos válidos obtenidos
                    }
                } catch (JSONException e) {
                    Log.e(TAG, "Error al analizar JSON: " + e.getMessage());
                }
            }

            if (ok) {
                Log.d(TAG, "Inicialización completada: datos desde el servidor");
                if (cb != null) cb.onListo(this, true);
            } else {
                Log.d(TAG, "Sin datos válidos del servidor, cargando ejemplo local");
                cargarPerfilEjemplo();
                if (cb != null) cb.onListo(this, false);
            }
        });
    }

    // ===================== Datos de ejemplo =====================
    private void cargarPerfilEjemplo() {
        this.nombre = "María López";
        if (this.correo == null || this.correo.isEmpty()) {
            this.correo = "maria@eolos.com"; // Si no hay correo, usar uno por defecto
        }
        this.tarjeta = "ABC123";
        this.contrasena = "password";
        this.fechaRegistro = new SimpleDateFormat("d/M/yyyy", Locale.getDefault()).format(new Date());
    }

    // ===================== Utilidades JSON =====================
    /** Convierte el objeto a JSON para enviarlo al backend. */
    public String toJson() {
        JSONObject o = new JSONObject();
        try {
            o.put("nombre", nvl(nombre));
            o.put("correo", nvl(correo));
            o.put("tarjeta", nvl(tarjeta));
            o.put("contrasena", nvl(contrasena));
            o.put("fecha", nvl(fechaRegistro));
        } catch (JSONException ignored) {}
        return o.toString();
    }

    /**
     * Analiza un JSON de manera segura.
     * Soporta estructura plana o anidada dentro de "data".
     * Solo se considera válido si al menos contiene nombre o correo.
     */
    private boolean fromJsonSeguro(String cuerpo) throws JSONException {
        JSONObject root = new JSONObject(cuerpo);
        JSONObject s = root;
        if (root.has("data") && root.opt("data") instanceof JSONObject) {
            s = root.getJSONObject("data");
        }

        String nombreNuevo = s.optString("nombre", null);
        String correoNuevo = s.optString("correo", null);
        String tarjetaNueva = s.optString("tarjeta", null);
        String contrasenaNueva = s.optString("contrasena", null);
        String fechaNueva = s.optString("fecha", s.optString("fechaRegistro", null));

        // Valido si hay al menos correo o nombre
        boolean valido = (correoNuevo != null && !correoNuevo.isEmpty()) ||
                (nombreNuevo != null && !nombreNuevo.isEmpty());

        if (valido) {
            if (nombreNuevo != null) this.nombre = nombreNuevo;
            if (correoNuevo != null) this.correo = correoNuevo;
            if (tarjetaNueva != null) this.tarjeta = tarjetaNueva;
            if (contrasenaNueva != null) this.contrasena = contrasenaNueva;
            if (fechaNueva != null) this.fechaRegistro = fechaNueva;
        }
        return valido;
    }

    private String nvl(String s) { return s == null ? "" : s; }

    // ===================== Lógica de guardado existente =====================
    /** Envía el perfil al servidor mediante POST (creación o guardado). */
    public void guardarPerfil() {
        String urlCompleta = BASE_URL + ENDPOINT_PERFIL;
        String cuerpoJson = toJson();

        Log.d(TAG, "➡️ POST: " + urlCompleta);
        Log.d(TAG, "📦 body: " + cuerpoJson);

        PeticionarioREST peticion = new PeticionarioREST();
        peticion.hacerPeticionREST("POST", urlCompleta, cuerpoJson, (codigo, cuerpo) -> {
            Log.d(TAG, "✅ POST resp: código=" + codigo + ", cuerpo=" + cuerpo);
        });
    }

    // ===================== Getters / Setters =====================
    public String getNombre() { return nombre; }
    public String getCorreo() { return correo; }
    public String getTarjeta() { return tarjeta; }
    public String getContrasena() { return contrasena; }
    public String getFechaRegistro() { return fechaRegistro; }

    public void setNombre(String nombre) { this.nombre = nombre; }
    public void setCorreo(String correo) { this.correo = correo; }
    public void setTarjeta(String tarjeta) { this.tarjeta = tarjeta; }
    public void setContrasena(String contrasena) { this.contrasena = contrasena; }
    public void setFechaRegistro(String fechaRegistro) { this.fechaRegistro = fechaRegistro; }

    @Override
    public String toString() {
        return "PerfilFake{" +
                "nombre='" + nombre + '\'' +
                ", correo='" + correo + '\'' +
                ", tarjeta='" + tarjeta + '\'' +
                ", contrasena='" + contrasena + '\'' +
                ", fechaRegistro='" + fechaRegistro + '\'' +
                '}';
    }
}
