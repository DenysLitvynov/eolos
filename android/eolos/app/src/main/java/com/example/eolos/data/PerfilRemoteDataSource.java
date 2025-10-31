/**
 * Archivo: PerfilRemoteDataSource.java
 * Descripción: Fuente de datos que combina conexión remota (REST)
 *              con almacenamiento local (SharedPreferences).
 *              Si el servidor no responde, usa los datos locales
 *              o un perfil falso (PerfilFake) como respaldo.
 */
package com.example.eolos.data;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;

import com.example.eolos.PeticionarioREST;
import com.example.eolos.logica_fake.PerfilFake;

import org.json.JSONException;
import org.json.JSONObject;

public class PerfilRemoteDataSource {

    // Dirección base del servidor (debes cambiarla por la tuya)
    private static final String BASE_URL = "https://api.tu-servidor.com/";
    private static final String GET_URL  = BASE_URL + "perfil";
    private static final String POST_URL = BASE_URL + "perfil";

    // Preferencias locales para guardar los datos cuando no hay conexión
    private final SharedPreferences prefs;

    public PerfilRemoteDataSource(Context ctx) {
        this.prefs = ctx.getSharedPreferences("perfil_fake_prefs", Context.MODE_PRIVATE);
    }

    /**
     * Interfaz genérica de callback para recibir respuestas asíncronas.
     * @param <T> Tipo de dato esperado en la respuesta.
     */
    public interface Callback<T> {
        void onSuccess(T data, boolean fromFakeOrLocal); // true = sin conexión (modo local)
        void onError(String message);
    }

    /**
     * Obtiene el perfil del servidor si es posible;
     * en caso contrario, carga desde SharedPreferences o usa PerfilFake.
     */
    public void getPerfil(Callback<PerfilDto> cb) {
        new PeticionarioREST().hacerPeticionREST("GET", GET_URL, null, (codigo, cuerpo) -> {
            try {
                if (codigo >= 200 && codigo < 300 && cuerpo != null && !cuerpo.isEmpty()) {
                    // Caso: respuesta correcta del servidor
                    PerfilDto dto = parseDto(cuerpo);
                    guardarPerfilLocal(dto);                  // Guarda copia local
                    post(() -> cb.onSuccess(dto, false));     // false = datos remotos
                } else {
                    // Caso: error o sin conexión → usa datos locales
                    PerfilDto dto = cargarPerfilLocal();
                    post(() -> cb.onSuccess(dto, true));
                }
            } catch (Exception e) {
                PerfilDto dto = cargarPerfilLocal();
                post(() -> cb.onSuccess(dto, true));
            }
        });
    }

    /**
     * Guarda el perfil en el servidor.
     * Si la conexión falla, guarda localmente.
     */
    public void savePerfil(PerfilDto dto, Callback<Boolean> cb) {
        String body = toJson(dto);
        new PeticionarioREST().hacerPeticionREST("POST", POST_URL, body, (codigo, cuerpo) -> {
            boolean ok = (codigo >= 200 && codigo < 300);
            if (ok) {
                guardarPerfilLocal(dto);                       // También actualiza caché local
                post(() -> cb.onSuccess(true, false));         // false = guardado remoto
            } else {
                guardarPerfilLocal(dto);                       // Guarda en local (sin conexión)
                post(() -> cb.onSuccess(true, true));          // true = guardado local
            }
        });
    }

    // ------------------- Métodos auxiliares -------------------

    /** Convierte un JSON recibido en un objeto PerfilDto */
    private PerfilDto parseDto(String json) throws JSONException {
        JSONObject o = new JSONObject(json);
        PerfilDto d = new PerfilDto();
        d.nombre = o.optString("nombre", "");
        d.correo = o.optString("correo", "");
        d.tarjeta = o.optString("tarjeta", "");
        d.contrasena = o.optString("contrasena", "");
        d.fecha = o.optString("fecha", "");
        return d;
    }

    /** Convierte un objeto PerfilDto a JSON */
    private String toJson(PerfilDto d) {
        JSONObject o = new JSONObject();
        try {
            o.put("nombre", d.nombre);
            o.put("correo", d.correo);
            o.put("tarjeta", d.tarjeta);
            o.put("contrasena", d.contrasena);
            o.put("fecha", d.fecha);
        } catch (JSONException ignored) {}
        return o.toString();
    }

    /**
     * Carga el perfil desde las preferencias locales.
     * Si no hay datos guardados, devuelve un PerfilFake.
     */
    private PerfilDto cargarPerfilLocal() {
        String nombre = prefs.getString("nombre", null);
        if (nombre != null) {
            PerfilDto dto = new PerfilDto();
            dto.nombre = nombre;
            dto.correo = prefs.getString("correo", "");
            dto.tarjeta = prefs.getString("tarjeta", "");
            dto.contrasena = prefs.getString("contrasena", "");
            dto.fecha = prefs.getString("fecha", "");
            return dto;
        }
        PerfilFake fake = new PerfilFake();
        return new PerfilDto(fake.getNombre(), fake.getCorreo(), fake.getTarjeta(),
                fake.getContrasena(), fake.getFechaRegistro());
    }

    /** Guarda el perfil actual en SharedPreferences */
    private void guardarPerfilLocal(PerfilDto d) {
        prefs.edit()
                .putString("nombre", d.nombre)
                .putString("correo", d.correo)
                .putString("tarjeta", d.tarjeta)
                .putString("contrasena", d.contrasena)
                .putString("fecha", d.fecha)
                .apply();
    }

    /** Ejecuta un runnable en el hilo principal (UI thread) */
    private void post(Runnable r) {
        new Handler(Looper.getMainLooper()).post(r);
    }
}
