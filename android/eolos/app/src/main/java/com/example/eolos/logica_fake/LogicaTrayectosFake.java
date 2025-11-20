package com.example.eolos.logica_fake;

import android.content.Context;
import android.location.Location;
import android.location.LocationManager;
import android.location.LocationListener;
import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import androidx.core.content.ContextCompat;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.example.eolos.PeticionarioREST;

import org.json.JSONObject;
import org.json.JSONException;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

public class LogicaTrayectosFake {

    private static final String TAG = "LogicaTrayectosFake";
    private static final String BASE_URL = "http://192.168.1.133:8000";
    private final Context context;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final LocationManager locationManager;
    private Location currentLocation;

    private String trayectoId = null;
    private String placaId = null;
    private String bicicletaId = null;

    private Runnable placaRunnable;

    // Singleton instance
    private static LogicaTrayectosFake instance;

    // Listener para actualizaciones de ubicación
    private final LocationListener locationListener = new LocationListener() {
        @Override
        public void onLocationChanged(Location location) {
            currentLocation = location;
            Log.d(TAG, "📍 Ubicación actualizada: " + location.getLatitude() + ", " + location.getLongitude());
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {}

        @Override
        public void onProviderEnabled(String provider) {}

        @Override
        public void onProviderDisabled(String provider) {}
    };

    // Constructor privado para Singleton
    private LogicaTrayectosFake(Context context) {
        this.context = context.getApplicationContext();
        this.locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE);
        iniciarActualizacionesUbicacion();
    }

    // Método Singleton
    public static synchronized LogicaTrayectosFake getInstance(Context context) {
        if (instance == null) {
            instance = new LogicaTrayectosFake(context);
        }
        return instance;
    }

    // Método para resetear la instancia (al desconectar)
    public static void resetInstance() {
        if (instance != null) {
            instance.detenerActualizacionesCompletas();
            instance = null;
            Log.i(TAG, "🔄 Instancia de LogicaTrayectosFake reseteada");
        }
    }

    // ==================================================================
    // INICIAR ACTUALIZACIONES DE UBICACIÓN
    // ==================================================================
    private void iniciarActualizacionesUbicacion() {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {

            try {
                // Obtener última ubicación conocida
                Location lastLocation = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
                if (lastLocation == null) {
                    lastLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                }
                if (lastLocation != null) {
                    currentLocation = lastLocation;
                }

                // Solicitar actualizaciones continuas
                locationManager.requestLocationUpdates(
                        LocationManager.GPS_PROVIDER,
                        5000,  // 5 segundos
                        10,    // 10 metros
                        locationListener
                );

                locationManager.requestLocationUpdates(
                        LocationManager.NETWORK_PROVIDER,
                        5000,
                        10,
                        locationListener
                );

                Log.i(TAG, "📍 Servicio de ubicación iniciado");

            } catch (SecurityException e) {
                Log.e(TAG, "❌ Sin permisos para acceder a la ubicación", e);
            }
        } else {
            Log.w(TAG, "⚠️ No hay permisos de ubicación");
        }
    }

    // ==================================================================
    // 1. INICIAR TRAYECTO
    // ==================================================================
    public void iniciarTrayecto(String bicicletaId) {
        this.bicicletaId = bicicletaId;

        JSONObject origen = getPosicionActual();
        if (origen == null) {
            Log.e(TAG, "❌ No se pudo obtener ubicación GPS para iniciar trayecto");
            return;
        }

        String fechaInicio = getFechaISO();

        // Obtener targeta_id del usuario desde SharedPreferences
        String targetaId = obtenerTargetaIdUsuario();
        if (targetaId == null) {
            Log.e(TAG, "❌ No se pudo obtener targeta_id del usuario");
            return;
        }

        JSONObject body = new JSONObject();
        try {
            body.put("targeta_id", targetaId);
            body.put("bicicleta_id", bicicletaId);
            body.put("fecha_inicio", fechaInicio);
            body.put("origen", origen);
        } catch (JSONException e) {
            Log.e(TAG, "❌ Error creando JSON iniciar trayecto", e);
            return;
        }

        String url = BASE_URL + "/api/v1/trayectos/iniciar-trayecto";

        Log.d(TAG, "🚀 ========== INICIANDO PETICIÓN INICIAR-TRAYECTO ==========");
        Log.d(TAG, "📤 URL: " + url);
        Log.d(TAG, "📤 MÉTODO: POST");
        Log.d(TAG, "📤 BODY COMPLETO:");
        Log.d(TAG, "📤 " + body.toString());
        Log.d(TAG, "📤 targeta_id: " + targetaId);
        Log.d(TAG, "📤 bicicleta_id: " + bicicletaId);
        Log.d(TAG, "📤 fecha_inicio: " + fechaInicio);
        Log.d(TAG, "📤 origen: " + origen.toString());
        Log.d(TAG, "🚀 =======================================================");

        new PeticionarioREST().hacerPeticionREST("POST", url, body.toString(), new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {
                Log.d(TAG, "📥 ========== RESPUESTA INICIAR-TRAYECTO ==========");
                Log.d(TAG, "📥 CÓDIGO HTTP: " + codigo);
                Log.d(TAG, "📥 CUERPO RESPUESTA: " + cuerpo);
                Log.d(TAG, "📥 ===============================================");

                if (codigo == 200) {
                    try {
                        JSONObject res = new JSONObject(cuerpo);
                        trayectoId = res.getString("trayecto_id");
                        Log.i(TAG, "✅ Trayecto iniciado correctamente: " + trayectoId);

                        // 2. OBTENER DATOS DEL TRAYECTO (siguiente paso)
                        obtenerDatosTrayecto();
                    } catch (Exception e) {
                        Log.e(TAG, "❌ Error parseando respuesta iniciar-trayecto", e);
                    }
                } else {
                    Log.e(TAG, "❌ Error iniciar trayecto: " + codigo + " → " + cuerpo);
                }
            }
        });
    }

    // ==================================================================
    // 2. OBTENER DATOS DEL TRAYECTO
    // ==================================================================
    private void obtenerDatosTrayecto() {
        if (trayectoId == null) {
            Log.e(TAG, "❌ No hay trayectoId para obtener datos");
            return;
        }

        String url = BASE_URL + "/api/v1/trayectos/obtener-datos-trayecto/" + trayectoId;

        Log.d(TAG, "🚀 ========== INICIANDO PETICIÓN OBTENER-DATOS-TRAYECTO ==========");
        Log.d(TAG, "📤 URL: " + url);
        Log.d(TAG, "📤 MÉTODO: GET");
        Log.d(TAG, "📤 trayecto_id: " + trayectoId);
        Log.d(TAG, "🚀 ============================================================");

        new PeticionarioREST().hacerPeticionREST("GET", url, null, new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {
                Log.d(TAG, "📥 ========== RESPUESTA OBTENER-DATOS-TRAYECTO ==========");
                Log.d(TAG, "📥 CÓDIGO HTTP: " + codigo);
                Log.d(TAG, "📥 CUERPO RESPUESTA: " + cuerpo);
                Log.d(TAG, "📥 ====================================================");

                if (codigo == 200) {
                    try {
                        JSONObject res = new JSONObject(cuerpo);
                        placaId = res.getString("placa_id");
                        Log.i(TAG, "✅ Datos recibidos - placa_id: " + placaId);
                        Log.i(TAG, "✅ TRAYECTO COMPLETAMENTE INICIALIZADO - Estado: " + getEstadoActual());

                        // 3. ACTUALIZAR ESTADO BICICLETA A "en_uso"
                        actualizarEstadoBicicleta("en_uso");

                        // 4. INICIAR ACTUALIZACIONES PERIÓDICAS
                        iniciarActualizacionesPeriodicas();
                    } catch (Exception e) {
                        Log.e(TAG, "❌ Error parseando obtener-datos-trayecto", e);
                    }
                } else {
                    Log.e(TAG, "❌ Error obtener datos: " + codigo + " → " + cuerpo);
                }
            }
        });
    }

    // ==================================================================
    // 3. ACTUALIZAR ESTADO BICICLETA
    // ==================================================================
    public void actualizarEstadoBicicleta(String estado) {
        if (bicicletaId == null) {
            Log.w(TAG, "⚠️ No hay bicicleta_id para actualizar estado");
            return;
        }

        JSONObject posicion = getPosicionActual();
        if (posicion == null) {
            Log.e(TAG, "❌ No se pudo obtener ubicación para actualizar estado bicicleta");
            return;
        }

        JSONObject body = new JSONObject();
        try {
            body.put("bicicleta_id", bicicletaId);
            body.put("estado", estado);
            body.put("posicion", posicion);
        } catch (JSONException e) {
            Log.e(TAG, "❌ Error JSON actualizar bicicleta", e);
            return;
        }

        String url = BASE_URL + "/api/v1/trayectos/actualizar-estado-bici";

        Log.d(TAG, "🚀 ========== INICIANDO PETICIÓN ACTUALIZAR-ESTADO-BICI ==========");
        Log.d(TAG, "📤 URL: " + url);
        Log.d(TAG, "📤 MÉTODO: PUT");
        Log.d(TAG, "📤 BODY COMPLETO:");
        Log.d(TAG, "📤 " + body.toString());
        Log.d(TAG, "📤 bicicleta_id: " + bicicletaId);
        Log.d(TAG, "📤 estado: " + estado);
        Log.d(TAG, "📤 posicion: " + posicion.toString());
        Log.d(TAG, "🚀 =============================================================");

        new PeticionarioREST().hacerPeticionREST("PUT", url, body.toString(), new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {
                Log.d(TAG, "📥 ========== RESPUESTA ACTUALIZAR-ESTADO-BICI ==========");
                Log.d(TAG, "📥 CÓDIGO HTTP: " + codigo);
                Log.d(TAG, "📥 CUERPO RESPUESTA: " + cuerpo);
                Log.d(TAG, "📥 =====================================================");

                if (codigo == 200) {
                    Log.i(TAG, "✅ Estado bicicleta actualizado a '" + estado + "'");
                } else {
                    Log.e(TAG, "❌ Error actualizando estado bicicleta: " + codigo + " → " + cuerpo);
                }
            }
        });
    }

    // ==================================================================
    // 4. ACTUALIZACIONES PERIÓDICAS
    // ==================================================================
    private void iniciarActualizacionesPeriodicas() {
        Log.i(TAG, "🔄 Iniciando actualizaciones periódicas cada 30 segundos");

        placaRunnable = new Runnable() {
            @Override
            public void run() {
                if (placaId != null) {
                    actualizarEstadoPlaca();
                }
                handler.postDelayed(this, 30000); // cada 30 segundos
            }
        };
        handler.post(placaRunnable);
    }

    private void actualizarEstadoPlaca() {
        if (placaId == null) {
            Log.w(TAG, "⚠️ No hay placa_id para actualizar estado");
            return;
        }

        JSONObject body = new JSONObject();
        try {
            body.put("placa_id", placaId);
            body.put("estado", "activa");
            body.put("ult_actualizacion_estado", getFechaISO());
        } catch (JSONException e) {
            Log.e(TAG, "❌ Error creando JSON actualizar placa", e);
            return;
        }

        String url = BASE_URL + "/api/v1/trayectos/actualizar-estado-placa";

        Log.d(TAG, "🔄 ========== ACTUALIZANDO ESTADO PLACA ==========");
        Log.d(TAG, "📤 URL: " + url);
        Log.d(TAG, "📤 MÉTODO: PUT");
        Log.d(TAG, "📤 BODY: " + body.toString());
        Log.d(TAG, "🔄 =============================================");

        new PeticionarioREST().hacerPeticionREST("PUT", url, body.toString(), new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {
                if (codigo == 200) {
                    Log.d(TAG, "✅ Estado placa actualizado correctamente");
                } else {
                    Log.e(TAG, "❌ Error actualizando estado placa: " + codigo + " → " + cuerpo);
                }
            }
        });
    }

    // ==================================================================
    // GUARDAR MEDIDA DESDE BEACON
    // ==================================================================
    public void guardarMedidaDesdeBeacon(String jsonTrama) {
        Log.d(TAG, "🔍 Estado actual al recibir medida: " + getEstadoActual());

        if (!estaCompletamenteInicializado()) {
            Log.w(TAG, "⚠️ Trayecto no completamente inicializado. Estado: " + getEstadoActual());

            // Reintentar después de 3 segundos si el trayecto está activo pero falta placa
            if (trayectoId != null && placaId == null) {
                Log.d(TAG, "🔄 Reintentando guardar medida en 3 segundos...");
                handler.postDelayed(() -> guardarMedidaDesdeBeacon(jsonTrama), 3000);
            }
            return;
        }

        try {
            JSONObject trama = new JSONObject(jsonTrama);
            double valor = trama.getDouble("valor_medido");
            int tipoMedicion = trama.getInt("tipo_medicion");

            String tipo;
            if (tipoMedicion == 11) {
                tipo = "pm2_5";
            } else if (tipoMedicion == 12) {
                tipo = "pm10";
            } else if (tipoMedicion == 13) {
                tipo = "co2";
            } else {
                tipo = "desconocido";
                Log.w(TAG, "⚠️ Tipo de medición desconocido: " + tipoMedicion);
                return;
            }

            JSONObject posicion = getPosicionActual();
            if (posicion == null) {
                Log.e(TAG, "❌ No se pudo obtener ubicación para guardar medida");
                return;
            }

            JSONObject body = new JSONObject();
            body.put("trayecto_id", trayectoId);
            body.put("placa_id", placaId);
            body.put("tipo", tipo);
            body.put("valor", valor);
            body.put("fecha_hora", getFechaISO());
            body.put("posicion", posicion);

            String url = BASE_URL + "/api/v1/trayectos/guardar-medida";

            Log.d(TAG, "📊 ========== GUARDANDO MEDIDA DESDE BEACON ==========");
            Log.d(TAG, "📤 URL: " + url);
            Log.d(TAG, "📤 MÉTODO: POST");
            Log.d(TAG, "📤 BODY: " + body.toString());
            Log.d(TAG, "📊 ==================================================");

            new PeticionarioREST().hacerPeticionREST("POST", url, body.toString(), new PeticionarioREST.RespuestaREST() {
                @Override
                public void callback(int codigo, String cuerpo) {
                    Log.d(TAG, "📥 ========== RESPUESTA GUARDAR-MEDIDA ==========");
                    Log.d(TAG, "📥 CÓDIGO HTTP: " + codigo);
                    Log.d(TAG, "📥 CUERPO RESPUESTA: " + cuerpo);
                    Log.d(TAG, "📥 ============================================");

                    if (codigo == 200) {
                        Log.i(TAG, "✅ Medida guardada correctamente: " + valor + " (" + tipo + ")");
                    } else {
                        Log.e(TAG, "❌ Error al guardar medida: " + codigo + " → " + cuerpo);
                    }
                }
            });

        } catch (Exception e) {
            Log.e(TAG, "❌ Error procesando trama del beacon", e);
        }
    }

    // ==================================================================
    // 5. FINALIZAR TRAYECTO
    // ==================================================================
    public void finalizarTrayecto() {
        Log.i(TAG, "🏁 Iniciando finalización del trayecto. Estado: " + getEstadoActual());

        if (trayectoId == null) {
            Log.w(TAG, "⚠️ No hay trayecto activo para finalizar");
            return;
        }

        detenerActualizacionesCompletas();

        JSONObject destino = getPosicionActual();
        if (destino == null) {
            Log.e(TAG, "❌ No se pudo obtener ubicación para destino");
            return;
        }

        JSONObject body = new JSONObject();
        try {
            body.put("trayecto_id", trayectoId);
            body.put("fecha_fin", getFechaISO());
            body.put("destino", destino);
        } catch (JSONException e) {
            Log.e(TAG, "❌ Error JSON finalizar trayecto", e);
            return;
        }

        String url = BASE_URL + "/api/v1/trayectos/finalizar-trayecto";

        Log.d(TAG, "🏁 ========== FINALIZANDO TRAYECTO ==========");
        Log.d(TAG, "📤 URL: " + url);
        Log.d(TAG, "📤 MÉTODO: PUT");
        Log.d(TAG, "📤 BODY COMPLETO:");
        Log.d(TAG, "📤 " + body.toString());
        Log.d(TAG, "📤 trayecto_id: " + trayectoId);
        Log.d(TAG, "📤 fecha_fin: " + getFechaISO());
        Log.d(TAG, "📤 destino: " + destino.toString());
        Log.d(TAG, "🏁 =========================================");

        new PeticionarioREST().hacerPeticionREST("PUT", url, body.toString(), new PeticionarioREST.RespuestaREST() {
            @Override
            public void callback(int codigo, String cuerpo) {
                Log.d(TAG, "📥 ========== RESPUESTA FINALIZAR-TRAYECTO ==========");
                Log.d(TAG, "📥 CÓDIGO HTTP: " + codigo);
                Log.d(TAG, "📥 CUERPO RESPUESTA: " + cuerpo);
                Log.d(TAG, "📥 =================================================");

                if (codigo == 200) {
                    Log.i(TAG, "✅ Trayecto finalizado correctamente");

                    // Actualizar estado de la bicicleta a "estacionada"
                    actualizarEstadoBicicleta("estacionada");
                } else {
                    Log.e(TAG, "❌ Error finalizando trayecto: " + codigo + " → " + cuerpo);
                }

                // Limpiar estado independientemente del resultado
                limpiarEstadoCompleto();
            }
        });
    }

    private void detenerActualizacionesCompletas() {
        Log.i(TAG, "🛑 Deteniendo todas las actualizaciones...");

        if (placaRunnable != null) {
            handler.removeCallbacks(placaRunnable);
            placaRunnable = null;
            Log.i(TAG, "✅ Actualizaciones periódicas detenidas");
        }

        // Detener actualizaciones de ubicación
        try {
            locationManager.removeUpdates(locationListener);
            Log.i(TAG, "✅ Actualizaciones de ubicación detenidas");
        } catch (SecurityException e) {
            Log.e(TAG, "❌ Error deteniendo actualizaciones de ubicación", e);
        }
    }

    private void limpiarEstadoCompleto() {
        Log.i(TAG, "🧹 Limpiando estado completo del trayecto");
        trayectoId = null;
        placaId = null;
        bicicletaId = null;
        Log.i(TAG, "✅ Estado limpiado: " + getEstadoActual());
    }

    // ==================================================================
    // OBTENER POSICIÓN ACTUAL
    // ==================================================================
    private JSONObject getPosicionActual() {
        try {
            if (currentLocation != null) {
                JSONObject pos = new JSONObject();
                pos.put("lat", currentLocation.getLatitude());
                pos.put("lon", currentLocation.getLongitude());
                Log.d(TAG, "📍 Usando ubicación actual: " + pos.toString());
                return pos;
            } else {
                // Si no hay ubicación actual, intentar obtener una última conocida
                if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)
                        == PackageManager.PERMISSION_GRANTED) {

                    Location lastLocation = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
                    if (lastLocation == null) {
                        lastLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                    }
                    if (lastLocation != null) {
                        JSONObject pos = new JSONObject();
                        pos.put("lat", lastLocation.getLatitude());
                        pos.put("lon", lastLocation.getLongitude());
                        Log.d(TAG, "📍 Usando última ubicación conocida: " + pos.toString());
                        return pos;
                    }
                }

                // Último recurso: posición por defecto
                Log.w(TAG, "⚠️ Usando posición por defecto (Madrid)");
                JSONObject pos = new JSONObject();
                pos.put("lat", 40.4168);
                pos.put("lon", -3.7038);
                return pos;
            }
        } catch (Exception e) {
            Log.e(TAG, "❌ Error obteniendo ubicación", e);
            return null;
        }
    }

    // ==================================================================
    // OBTENER TARJETA ID DEL USUARIO
    // ==================================================================
    private String obtenerTargetaIdUsuario() {
        try {
            android.content.SharedPreferences prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE);
            String targetaId = prefs.getString("targeta_id", null);

            if (targetaId != null && !targetaId.trim().isEmpty()) {
                Log.d(TAG, "🎫 Usando targeta_id de SharedPreferences: " + targetaId);
                return targetaId.trim();
            } else {
                Log.w(TAG, "⚠️ No hay targeta_id en SharedPreferences, usando valor por defecto");
                return "12345678Z";
            }
        } catch (Exception e) {
            Log.e(TAG, "❌ Error obteniendo targeta_id", e);
            return "12345678Z";
        }
    }

    // ==================================================================
    // UTILIDADES
    // ==================================================================
    private String getFechaISO() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US);
        sdf.setTimeZone(TimeZone.getTimeZone("UTC"));
        return sdf.format(new Date());
    }

    public boolean estaActivo() {
        return trayectoId != null;
    }

    /**
     * Verifica si el trayecto está completamente inicializado
     */
    public boolean estaCompletamenteInicializado() {
        return trayectoId != null && placaId != null && bicicletaId != null;
    }

    /**
     * Obtiene el estado actual para debugging
     */
    public String getEstadoActual() {
        return String.format("Trayecto: %s, Placa: %s, Bici: %s",
                trayectoId != null ? trayectoId.substring(0, 8) + "..." : "null",
                placaId != null ? placaId.substring(0, 8) + "..." : "null",
                bicicletaId != null ? bicicletaId : "null");
    }

    public String getTrayectoId() {
        return trayectoId;
    }

    public String getPlacaId() {
        return placaId;
    }

    public String getBicicletaId() {
        return bicicletaId;
    }
}