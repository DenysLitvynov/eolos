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

/**
 * @RecompensaFake.java
 * @Autor: Ariel Bejaran
 * @Desc: Actividad android que carga y permite descargar el qr de la recompensa
 * @Fecha: 7/01/2026
 */
public class RecompensasFake {

    // Configuración de rutas
    private static final String BASE_URL = "http://10.131.251.51:8000";
    private static final String API_PREFIX = "/api/v1";
    private static final String ENDPOINT_RECOMPENSAS = "/recompensas";
    private static String url_api_recompensas = BASE_URL + API_PREFIX + ENDPOINT_RECOMPENSAS;

    public interface RecompensasCallback {
        void onSuccess(List<Recompensa_Item> recompensas);
        void onError(String error);
    }

    public interface Km_acumulado_Callback {
        void onResult(double km);
        void onError(String error);
    }

    /**
     * @method seleccionarLogoPorTitulo
     * @description Implementa una lógica de selección dinámica que asigna un recurso gráfico (ID de drawable)
     * basándose en palabras clave detectadas en el título de la recompensa.
     * @param {String} titulo - Nombre de la recompensa a evaluar.
     * @returns {int} ID del recurso gráfico (R.drawable) correspondiente.
     */
    private int seleccionarLogoPorTitulo(String titulo) {
        if (titulo == null) return R.drawable.regalo; // Por defecto

        String t = titulo.toLowerCase();

        if (t.contains("café") || t.contains("cafe")) {
            return R.drawable.cafe; // Asegúrate de tener estos iconos o usa emojis en un TextView
        } else if (t.contains("burger") || t.contains("menú") || t.contains("mcmenú")) {
            return R.drawable.burger;
        } else if (t.contains("cine") || t.contains("película")) {
            return R.drawable.peli;
        }

        return R.drawable.regalo; // Fallback
    }
    // -----------------------------------------------------------------

    /**
     * @method getToken
     * @description Recupera el token de autenticación almacenado de forma persistente en SharedPreferences
     * para validar las peticiones hacia la API.
     * @param {Context} context - Contexto de la aplicación necesario para acceder a las preferencias.
     * @returns {String} Token de acceso o null si no existe.
     */
    private String getToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);
        Log.d("EOLOS_DEBUG", "Token recuperado de SharedPreferences: " + (token != null ? "SÍ" : "NULL"));
        return token;
    }

    /**
     * @method obtener_km_acumulados
     * @description Realiza una petición GET autenticada al servidor para obtener la distancia total
     * recorrida por el usuario y la devuelve a través de un callback.
     * @param {Context} context - Contexto para obtención del token.
     * @param {Km_acumulado_Callback} callback - Interfaz para gestionar la respuesta de éxito o error.
     */
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
    /**
     * @method obtenerTodasLasRecompensas
     * @description Solicita al endpoint REST el listado completo de recompensas, procesa el JSON recibido
     * mapeando cada elemento al modelo Recompensa_Item e integrando la lógica de logos dinámicos.
     * @param {Context} context - Contexto para autenticación de la petición.
     * @param {RecompensasCallback} callback - Interfaz que retorna la lista procesada o el mensaje de fallo.
     */
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
                        String titulo = json.getString("titulo");
                        int logoDinamico = seleccionarLogoPorTitulo(titulo);
                        recompensas.add(new Recompensa_Item(
                                logoDinamico,
                                titulo,
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