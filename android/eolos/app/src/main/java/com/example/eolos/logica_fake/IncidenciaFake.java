package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONException;
import org.json.JSONObject;

public class IncidenciaFake {

    private static final String TAG = "IncidenciaFake";

    private static final String BASE_URL = "http://10.0.2.2:8000";
    private static final String ENDPOINT_INCIDENCIAS = "/api/v1/incidencias";

    // Callback para devolver el resultado de la petición
    public interface Callback {
        void onResult(boolean exito, int codigo, String cuerpo);
    }

    private final Context context;

    public IncidenciaFake(Context context) {
        this.context = context.getApplicationContext();
    }

    /**
     * Crea una incidencia usando JWT:
     *  - el usuario_id lo obtiene el backend a partir del token
     *  - enviamos short_code (VLC001...), descripcion y fuente ("admin"/"app")
     */
    public void crearIncidencia(String bikeCode, String descripcion, String fuente, Callback cb) {

        // Recuperamos el token JWT guardado en SharedPreferences
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        // Si no hay token → no se puede realizar la petición autenticada
        if (token == null || token.trim().isEmpty()) {
            Log.w(TAG, "Sin token JWT, no se puede crear incidencia");
            if (cb != null) cb.onResult(false, 401, "Sin token JWT");
            return;
        }

        // Construimos el objeto JSON que enviaremos en el cuerpo de la petición
        JSONObject json = new JSONObject();
        try {
            json.put("short_code", bikeCode);               // Código de la bicicleta (VLC001 / VLC045)
            json.put("descripcion", descripcion);           // Descripción generada en la Activity
            json.put("fuente", fuente.toLowerCase());       // Origen: "admin" o "app"
        } catch (JSONException e) {
            Log.e(TAG, "Error creando JSON: " + e.getMessage());
            if (cb != null) cb.onResult(false, 0, "Error JSON");
            return;
        }

        String url = BASE_URL + ENDPOINT_INCIDENCIAS;
        Log.d(TAG, "➡️ POST " + url);
        Log.d(TAG, "📦 body: " + json.toString());

        // Usamos PeticionarioREST para hacer una petición HTTP con autenticación
        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth(
                "POST",
                url,
                json.toString(),
                token,
                (codigo, cuerpo) -> {
                    Log.d(TAG, "resp code=" + codigo + ", body=" + cuerpo);
                    boolean exito = (codigo >= 200 && codigo < 300);
                    if (cb != null) cb.onResult(exito, codigo, cuerpo);
                }
        );
    }
}
