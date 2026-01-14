package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.PeticionarioREST;
import com.example.eolos.R;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class RecompensasFake {

    // Configuración de rutas
    private static final String BASE_URL = "http://192.168.18.199:8000";
    private static final String API_PREFIX = "/api/v1";
    private static final String ENDPOINT_RECOMPENSAS = "/recompensas";
    private static String url_api_recompensas = BASE_URL + API_PREFIX + ENDPOINT_RECOMPENSAS;

    // --- INTERFACES (Esto es lo que faltaba y causaba los errores) ---
    public interface RecompensasCallback {
        void onSuccess(List<Recompensa_Item> recompensas);
        void onError(String error);
    }

    public interface Km_acumulado_Callback {
        void onResult(double km);
        void onError(String error);
    }
    // -----------------------------------------------------------------

    private String getToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);
        Log.d("EOLOS_DEBUG", "Token recuperado de SharedPreferences: " + (token != null ? "SÍ" : "NULL"));
        return token;
    }

    public void obtener_km_acumulados(Context context, Km_acumulado_Callback callback) {
        PeticionarioREST peticionario = new PeticionarioREST();
        String url = BASE_URL + API_PREFIX + "/recompensas/obtener_distancia_acumulada";

        String tokenReal = getToken(context);

        Log.d("EOLOS_DEBUG", "Llamando a KM en URL: " + url);

        peticionario.hacerPeticionRESTconAuth("GET", url, null, tokenReal, (codigo, cuerpo) -> {
            Log.d("EOLOS_DEBUG", "KM Response Code: " + codigo);
            if (codigo == 200) {
                try {
                    JSONObject jsonObject = new JSONObject(cuerpo);
                    double kmAcumulados = jsonObject.getDouble("km_acumulados");
                    callback.onResult(kmAcumulados);
                } catch (Exception e) {
                    Log.e("EOLOS_DEBUG", "Error parseando KM: " + e.getMessage());
                    callback.onError("Error JSON KM: " + e.getMessage());
                }
            } else {
                Log.e("EOLOS_DEBUG", "Error de red KM. Código: " + codigo);
                callback.onError("Error servidor KM: " + codigo);
            }
        });
    }

    public void obtenerTodasLasRecompensas(Context context, RecompensasCallback callback) {
        PeticionarioREST peticionario = new PeticionarioREST();
        String url = url_api_recompensas + "/obtener_recompensas";

        String tokenReal = getToken(context);

        Log.d("EOLOS_DEBUG", "Llamando a Recompensas en URL: " + url);

        peticionario.hacerPeticionRESTconAuth("GET", url, null, tokenReal, (codigo, cuerpo) -> {
            Log.d("EOLOS_DEBUG", "Rewards Response Code: " + codigo);
            if (codigo == 200) {
                try {
                    JSONArray jsonArray = new JSONArray(cuerpo);
                    List<Recompensa_Item> recompensas = new ArrayList<>();
                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject json = jsonArray.getJSONObject(i);
                        recompensas.add(new Recompensa_Item(
                                R.drawable.logo_mcdonalds,
                                json.getString("titulo"),
                                json.optString("descripcion", ""),
                                json.getDouble("criterio_num_km")
                        ));
                    }
                    callback.onSuccess(recompensas);
                } catch (Exception e) {
                    Log.e("EOLOS_DEBUG", "Error parseando Recompensas: " + e.getMessage());
                    callback.onError("Error JSON: " + e.getMessage());
                }
            } else {
                Log.e("EOLOS_DEBUG", "Error de red Recompensas. Código: " + codigo);
                callback.onError("Error servidor recompensas: " + codigo);
            }
        });
    }
}