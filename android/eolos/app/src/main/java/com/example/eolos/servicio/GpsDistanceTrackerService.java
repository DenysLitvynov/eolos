//
//  GpsDistanceTrackerService.java
//  Servicio background – Medición GPS de distancia recorrida
//  Desde: pulsar "Conectar"  →  Hasta: pulsar "Desconectar"
//  Autor: Hugo Belda
//  Fecha: 19/11/2025
//

package com.example.eolos.servicio;

import android.app.Service;
import android.content.Intent;
import android.location.Location;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.google.android.gms.location.*;
import com.google.android.gms.location.FusedLocationProviderClient;

public class GpsDistanceTrackerService extends Service {

    private static final String TAG         = "GPS_DIST";
    public static final String ACCION_DETENER = "ACCION_DETENER";

    public static final String ACCION_ACTUALIZAR_DISTANCIA = "com.example.eolos.DISTANCE_UPDATE";
    public static final String ACCION_SERVICIO_DETENIDO  = "com.example.eolos.DISTANCE_SERVICE_STOPPED";
    public static final String EXTRA_DISTANCIA         = "distance_meters";

    private static boolean servicioEjecutandose = false;

    private FusedLocationProviderClient clienteUbicacionFusionada;
    private LocationCallback           callbackUbicacion;
    private Location                   ultimaUbicacion;
    private float                      distanciaTotalMetros = 0.0f;

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  onCreate()
    //  Inicializa FusedLocation y callback
    //------------------------------------------------------------------------------------------
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, ">>> SERVICIO GPS onCreate() <<<");
        clienteUbicacionFusionada = LocationServices.getFusedLocationProviderClient(this);
        construirCallbackUbicacion();
    }

    //------------------------------------------------------------------------------------------
    //  Intent?, int, int  →  int
    //  onStartCommand()
    //  Inicia o detiene el tracking GPS REAL
    //------------------------------------------------------------------------------------------
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, ">>> SERVICIO GPS onStartCommand() - Acción: " +
                (intent != null ? intent.getAction() : "null") + " <<<");

        if (intent != null && ACCION_DETENER.equals(intent.getAction())) {
            Log.d(TAG, "Recibida acción DETENER");
            detenerSeguimientoYTerminar();
            return START_NOT_STICKY;
        }

        if (servicioEjecutandose) {
            Log.d(TAG, "Servicio ya estaba ejecutándose");
            return START_STICKY;
        }

        Log.d(TAG, ">>> INICIANDO SERVICIO GPS POR PRIMERA VEZ <<<");
        servicioEjecutandose = true;

        // REINICIAMOS A CERO ANTES DE EMPEZAR
        distanciaTotalMetros = 0.0f;
        ultimaUbicacion = null;

        // INICIAR GPS REAL (SIN NOTIFICACIÓN)
        solicitarActualizacionesUbicacion();

        // Emitir distancia inicial
        emitirDistancia(0.0f);

        return START_STICKY;
    }

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  construirCallbackUbicacion()
    //  Define comportamiento ante cada nueva ubicación REAL con filtros mejorados
    //------------------------------------------------------------------------------------------
    private void construirCallbackUbicacion() {
        callbackUbicacion = new LocationCallback() {
            @Override
            public void onLocationResult(LocationResult resultado) {
                if (resultado == null) return;

                for (Location ubicacionActual : resultado.getLocations()) {
                    if (ubicacionActual == null) continue;

                    Log.d(TAG, "Nueva ubicación recibida - Lat: " + ubicacionActual.getLatitude() +
                            ", Lon: " + ubicacionActual.getLongitude() +
                            ", Precisión: " + ubicacionActual.getAccuracy() + "m");

                    if (ultimaUbicacion == null) {
                        ultimaUbicacion = ubicacionActual;
                        Log.d(TAG, "Primera ubicación establecida");
                        continue;
                    }

                    float distanciaCalculada = ultimaUbicacion.distanceTo(ubicacionActual);

                    // FILTROS MEJORADOS PARA MAYOR PRECISIÓN
                    boolean precisionAceptable = ubicacionActual.getAccuracy() < 15.0f;
                    boolean distanciaSignificativa = distanciaCalculada > 5.0f;
                    boolean mismaFuenteUbicacion = ultimaUbicacion.getProvider().equals(ubicacionActual.getProvider());

                    if (distanciaSignificativa && precisionAceptable && mismaFuenteUbicacion) {
                        distanciaTotalMetros += distanciaCalculada;
                        ultimaUbicacion = ubicacionActual;

                        Log.d(TAG, "Distancia añadida: " + distanciaCalculada + " metros - Total: " + distanciaTotalMetros);

                        emitirDistancia(distanciaTotalMetros);
                    } else {
                        Log.d(TAG, "Ubicación descartada - Dist: " + distanciaCalculada +
                                "m, Prec: " + ubicacionActual.getAccuracy() + "m, Fuente: " + ubicacionActual.getProvider());
                    }
                }
            }

            @Override
            public void onLocationAvailability(LocationAvailability disponibilidadUbicacion) {
                super.onLocationAvailability(disponibilidadUbicacion);
                if (disponibilidadUbicacion != null) {
                    Log.d(TAG, "Disponibilidad ubicación: " + disponibilidadUbicacion.isLocationAvailable());
                }
            }
        };
    }

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  solicitarActualizacionesUbicacion()
    //  Solicita actualizaciones de GPS REAL con alta precisión
    //------------------------------------------------------------------------------------------
    private void solicitarActualizacionesUbicacion() {
        try {
            LocationRequest solicitud = new LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 2000)
                    .setMinUpdateIntervalMillis(1000)
                    .setMinUpdateDistanceMeters(1.0f)
                    .build();

            clienteUbicacionFusionada.requestLocationUpdates(
                    solicitud,
                    callbackUbicacion,
                    Looper.getMainLooper()
            );

            Log.d(TAG, "GPS REAL solicitado correctamente - alta precisión, intervalo 2 segundos");

        } catch (SecurityException e) {
            Log.e(TAG, "Permiso de ubicación denegado", e);
            stopSelf();
        } catch (Exception e) {
            Log.e(TAG, "Error al solicitar ubicaciones", e);
            stopSelf();
        }
    }

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  detenerSeguimientoYTerminar()
    //  Finaliza GPS, emite distancia total y termina el servicio
    //------------------------------------------------------------------------------------------
    private void detenerSeguimientoYTerminar() {
        Log.d(TAG, "Deteniendo servicio GPS - Distancia final: " + distanciaTotalMetros + " metros");

        if (callbackUbicacion != null) {
            clienteUbicacionFusionada.removeLocationUpdates(callbackUbicacion);
            Log.d(TAG, "Actualizaciones de ubicación removidas");
        }

        Intent intentFinal = new Intent(ACCION_SERVICIO_DETENIDO);
        intentFinal.putExtra(EXTRA_DISTANCIA, distanciaTotalMetros);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intentFinal);

        stopSelf();
        servicioEjecutandose = false;

        Log.d(TAG, "Servicio GPS completamente detenido");
    }

    //------------------------------------------------------------------------------------------
    //  float  →  void
    //  emitirDistancia()
    //  Emite distancia actual vía LocalBroadcast a la actividad
    //------------------------------------------------------------------------------------------
    private void emitirDistancia(float metros) {
        Intent intentDistancia = new Intent(ACCION_ACTUALIZAR_DISTANCIA);
        intentDistancia.putExtra(EXTRA_DISTANCIA, metros);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intentDistancia);
        Log.d(TAG, "Broadcast enviado: " + metros + " metros");
    }

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  onDestroy()
    //  Limpieza final garantizada al destruir el servicio
    //------------------------------------------------------------------------------------------
    @Override
    public void onDestroy() {
        Log.d(TAG, ">>> SERVICIO GPS onDestroy() <<<");
        detenerSeguimientoYTerminar();
        super.onDestroy();
    }

    //------------------------------------------------------------------------------------------
    //  Intent  →  IBinder
    //  onBind()
    //  Servicio no enlazable → retorna null
    //------------------------------------------------------------------------------------------
    @Override
    public IBinder onBind(Intent intent) { return null; }

    //------------------------------------------------------------------------------------------
    //  void  →  boolean
    //  isRunning()
    //  Estado actual del servicio para verificación externa
    //------------------------------------------------------------------------------------------
    public static boolean isRunning() { return servicioEjecutandose; }
}