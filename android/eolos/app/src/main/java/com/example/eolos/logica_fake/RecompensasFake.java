package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;

import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.PeticionarioREST;
import com.example.eolos.R;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class RecompensasFake {

    private static final String BASE_URL = "http://192.168.18.199:8000";
    private static final String ENDPOINT_RECOMPENSAS = "/api/v1/recompensas";
    private static String url_api_recompensas= BASE_URL + ENDPOINT_RECOMPENSAS;

    // Función auxiliar para obtener el token
    private String getToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        return prefs.getString("token", null);
    }

    public interface RecompensasCallback {
        void onSuccess(List<Recompensa_Item> recompensas);
        void onError(String error);
    }

    public interface Km_acumulado_Callback {
        void onResult(double km);
        void onError(String error);
    }

    public void obtenerTodasLasRecompensas(RecompensasCallback callback) {
        PeticionarioREST peticionario = new PeticionarioREST();
        String obtener_recompensas_endpoint="/obtener_recompensas";
        String url = url_api_recompensas+obtener_recompensas_endpoint;

        // La petición a /recompensas es un GET
        peticionario.hacerPeticionRESTconAuth("GET", url, null,"aa", new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {

                if (codigo == 200) {
                    try {
                        JSONArray jsonArray = new JSONArray(cuerpo);
                        List<Recompensa_Item> recompensas = new ArrayList<>();

                        for (int i = 0; i < jsonArray.length(); i++) {
                            JSONObject jsonRecompensa = jsonArray.getJSONObject(i);
                            String titulo = jsonRecompensa.getString("titulo");
                            double crit_num_km = jsonRecompensa.getDouble("criterio_num_km");

                            // int iconoFijo = R.drawable.logo_mcdonalds; // Usamos un icono fijo por simplicidad

                            // Creamos un POJO (Recompensa_Item)
                            //TODO: Añadir mas datos si es necesario
                            Recompensa_Item item = new Recompensa_Item(R.drawable.logo_mcdonalds, titulo, crit_num_km);

                            recompensas.add(item);
                        }
                        callback.onSuccess(recompensas);
                    } catch (Exception e) {
                        callback.onError("Error procesando respuesta JSON: " + e.getMessage());
                    }
                } else {
                    callback.onError("Error de servidor: Código " + codigo);
                }
            }
        });
    }

    public void obtener_km_acumulados(Km_acumulado_Callback callback) {
        PeticionarioREST peticionario = new PeticionarioREST();
        String obtener_km_acumulados_endpoint="/obtener_distancia_acumulada";
        String url = url_api_recompensas+obtener_km_acumulados_endpoint;

        // La petición a /recompensas es un GET
        peticionario.hacerPeticionREST("GET", url, null, new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {

                if (codigo == 200) {
                    try {
                        // Esperamos un JSONObject, NO un JSONArray
                        JSONObject jsonObject = new JSONObject(cuerpo);

                        // Extraemos el campo clave de la respuesta de FastAPI
                        double kmAcumulados = jsonObject.getDouble("km_acumulados_este_mes");

                        // Llamamos al callback de éxito con el valor numérico
                        callback.onResult(kmAcumulados);

                    } catch (Exception e) {
                        callback.onError("Error procesando respuesta JSON para KM: " + e.getMessage());
                    }
                } else {
                    callback.onError("Error de servidor: Código " + codigo + ". Cuerpo: " + cuerpo);
                }
            }
        });
    }
}