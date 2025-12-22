package com.example.eolos.logica_fake;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * HomeFake (final)
 * GET /api/v1/home?lat=..&lon=.. (lat/lon opcional)
 */
public class HomeFake {

    private static final String TAG = "HomeFake";

    // ⚠️ 改成你自己的后端地址
    private static final String BASE_URL = "http://192.168.0.68:8000";
    private static final String ENDPOINT_HOME = "/api/v1/home";

    // ====== Datos parseados ======
    public static class GasItem {
        public String tipo;
        public Double valor;
    }

    private String nombreVisible;
    private String placaId;

    private String aqiScore;      // String: "--" o número
    private String aqiEstado;
    private String aqiDescripcion;

    private final List<GasItem> gases = new ArrayList<>();

    private int rutasLimpias;
    private double co2Kg;
    private int puntos;

    private Double ultimoDistKm;
    private Integer ultimoTiempoMin;
    private String ultimoCalidadPromedio;

    public interface Callback {
        void onResult(boolean ok, int code, String rawBody, HomeFake home);
    }

    private final Context context;

    public HomeFake(Context ctx) {
        this.context = ctx.getApplicationContext();
    }

    // ==========================================================
    // GET /home (lat/lon opcional)
    // ==========================================================
    public void cargarHome(Double lat, Double lon, Callback cb) {
        SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
        String token = prefs.getString("token", null);

        if (token == null || token.trim().isEmpty()) {
            if (cb != null) cb.onResult(false, 401, "Sin token", this);
            return;
        }

        String url = BASE_URL + ENDPOINT_HOME;
        if (lat != null && lon != null) url = url + "?lat=" + lat + "&lon=" + lon;

        Log.d(TAG, "➡️ GET " + url);

        PeticionarioREST peti = new PeticionarioREST();
        peti.hacerPeticionRESTconAuth("GET", url, null, token, (codigo, cuerpo) -> {
            Log.d(TAG, "GET resp = " + codigo + ", body=" + cuerpo);

            boolean ok = (codigo >= 200 && codigo < 300);
            if (ok) {
                try {
                    fromJsonServidor(cuerpo);
                } catch (JSONException e) {
                    Log.e(TAG, "Error JSON: " + e.getMessage());
                    ok = false;
                }
            }

            if (cb != null) cb.onResult(ok, codigo, cuerpo, this);
        });
    }

    // ==========================================================
    // JSON parse
    // ==========================================================
    private void fromJsonServidor(String cuerpo) throws JSONException {
        JSONObject root = new JSONObject(cuerpo);

        JSONObject usuario = root.optJSONObject("usuario");
        nombreVisible = usuario != null ? usuario.optString("nombre_visible", "Usuario") : "Usuario";

        placaId = root.optString("placa_id", null);

        JSONObject ca = root.optJSONObject("calidad_aire");
        if (ca != null) {
            Object sc = ca.opt("score");
            aqiScore = (sc == null) ? "--" : String.valueOf(sc);
            aqiEstado = ca.optString("estado", "--");
            aqiDescripcion = ca.optString("descripcion", "");
        } else {
            aqiScore = "--";
            aqiEstado = "--";
            aqiDescripcion = "";
        }

        // gases (todos los tipos)
        gases.clear();
        JSONObject nivel = root.optJSONObject("nivel_actual");
        if (nivel != null) {
            JSONArray arr = nivel.optJSONArray("gases");
            if (arr != null) {
                for (int i = 0; i < arr.length(); i++) {
                    JSONObject g = arr.optJSONObject(i);
                    if (g == null) continue;
                    GasItem it = new GasItem();
                    it.tipo = g.optString("tipo", "gas");
                    if (!g.isNull("valor")) it.valor = g.optDouble("valor");
                    gases.add(it);
                }
            }
        }

        JSONObject imp = root.optJSONObject("impacto");
        if (imp != null) {
            rutasLimpias = imp.optInt("rutas_limpias", 0);
            co2Kg = imp.optDouble("co2_kg", 0.0);
            puntos = imp.optInt("puntos", 0);
        } else {
            rutasLimpias = 0;
            co2Kg = 0.0;
            puntos = 0;
        }

        JSONObject ut = root.optJSONObject("ultimo_trayecto");
        if (ut != null) {
            ultimoDistKm = ut.isNull("distancia_km") ? null : ut.optDouble("distancia_km");
            ultimoTiempoMin = ut.isNull("tiempo_min") ? null : ut.optInt("tiempo_min");
            ultimoCalidadPromedio = ut.optString("calidad_promedio", null);
        } else {
            ultimoDistKm = null;
            ultimoTiempoMin = null;
            ultimoCalidadPromedio = null;
        }
    }

    // ==========================================================
    // Getters
    // ==========================================================
    public String getNombreVisible() { return nombreVisible; }
    public String getPlacaId() { return placaId; }

    public String getAqiScore() { return aqiScore; }
    public String getAqiEstado() { return aqiEstado; }
    public String getAqiDescripcion() { return aqiDescripcion; }

    public List<GasItem> getGases() { return gases; }

    public int getRutasLimpias() { return rutasLimpias; }
    public double getCo2Kg() { return co2Kg; }
    public int getPuntos() { return puntos; }

    public Double getUltimoDistKm() { return ultimoDistKm; }
    public Integer getUltimoTiempoMin() { return ultimoTiempoMin; }
    public String getUltimoCalidadPromedio() { return ultimoCalidadPromedio; }
}
