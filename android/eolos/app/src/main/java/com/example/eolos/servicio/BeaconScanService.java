/**
 * Fichero: BeaconScanService.java
 * Descripción: Servicio en primer plano para escaneo de beacons BLE.
 * Mantiene notificación persistente.
 * Envía broadcasts al detectar beacons.
 * Permite detener el escaneo mediante acción "Stop".
 * Autor: JINWEI
 * Editor: Hugo Belda
 * Fecha: 14/11/2025
 */
package com.example.eolos.servicio;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.core.app.NotificationCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.eolos.EscanerIBeacons;
import com.example.eolos.activities.MainActivity;
import com.example.eolos.logica_fake.LogicaFake;


// --------------------------------------------------------------------
// Servicio en primer plano para escaneo BLE
// --------------------------------------------------------------------
public class BeaconScanService extends Service {

    private String targetDeviceName;            // Nombre del beacon objetivo
    private EscanerIBeacons escanerIBeacons;    // Instancia de escaneo BLE
    private static final String TAG = "BeaconSvc";
    private static final String ACTION_STOP = "ACTION_STOP_BEACON_SCAN";
    private static final int NOTIF_ID = 1;
    private static boolean isRunning = false;   // Estado del servicio
    private String baseUrl = "http://192.168.1.25:8000";  // <- Solo cambia ESTO (IP + puerto).
    private String endpointGuardar = "/api/v1/guardar-medida";  // <- Endpoint específico

    // Timestamp de la última detección de beacon
    private static long lastDetectedTime = 0;

    /**
     * Inicialización del servicio.
     * Crea el canal de notificación si es necesario (Android O+).
     */
    @Override
    public void onCreate() {
        super.onCreate();
        ensureChannel();
    }

    // --------------------------------------------------------------------
    // Maneja comandos entrantes
    // --------------------------------------------------------------------
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        // 1. Detención vía acción "Stop" (desde notificación o UI)
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            Log.i(TAG, "Deteniendo servicio por botón");
            if (escanerIBeacons != null) {
                escanerIBeacons.destroy();
                escanerIBeacons = null;
            }
            stopForeground(true);
            stopSelf();
            isRunning = false;
            return START_NOT_STICKY;
        }

        // 2. StartForeground inmediata con notificación + acción "Detener"
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent contentPi = PendingIntent.getActivity(this, 100, openApp, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        // Intent para acción "Detener" en la notificación
        Intent stopIntent = new Intent(this, BeaconScanService.class);
        stopIntent.setAction(ACTION_STOP);
        PendingIntent stopPi = PendingIntent.getService(this, 101, stopIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        // Usar nuevo método con acción "Detener"
        Notification notification = NotificationHelper.buildForegroundNotificationWithStopAction(
                this,
                "Escaneando beacon...",
                "Enviando datos en segundo plano",
                contentPi,
                stopPi
        );

        startForeground(NOTIF_ID, notification);

        // 3. Validaciones post-startForeground
        if (isRunning) {
            Log.i(TAG, "Servicio ya corriendo");
            return START_STICKY;
        }

        if (intent == null || intent.getStringExtra("beacon_name") == null) {
            Log.e(TAG, "Sin parámetro 'beacon_name', deteniendo servicio");
            stopSelf();
            return START_NOT_STICKY;
        }

        String name = intent.getStringExtra("beacon_name").trim();
        if (name.isEmpty()) {
            Log.e(TAG, "Nombre de beacon vacío, deteniendo servicio");
            stopSelf();
            return START_NOT_STICKY;
        }

        // 4. Configuración del escaneo
        targetDeviceName = name;
        isRunning = true;
        Log.i(TAG, ">>> ESCANEANDO SOLO: " + targetDeviceName + " <<<");

        escanerIBeacons = EscanerIBeacons.getInstance(this, json -> {
            long ahora = System.currentTimeMillis();
            lastDetectedTime = ahora;
        });

        escanerIBeacons.iniciarEscaneoAutomatico(targetDeviceName);

        return START_STICKY;
    }

    // --------------------------------------------------------------------
    // Detiene el servicio y libera recursos
    // --------------------------------------------------------------------
    @Override
    public void onDestroy() {
        super.onDestroy();
        if (escanerIBeacons != null) {
            escanerIBeacons.destroy();
            escanerIBeacons = null;
        }
        // Cancelar la notificación al destruir el servicio
        NotificationHelper.cancel(this, NOTIF_ID);
        stopForeground(true);
        isRunning = false;
        Log.i(TAG, "Servicio detenido");
    }
    // --------------------------------------------------------------------
    // Servicio no enlazable
    // --------------------------------------------------------------------
    @Override
    public IBinder onBind(Intent intent) {
        // Servicio no enlazable
        return null;
    }

    // --------------------------------------------------------------------
    // Crear canal de notificación (Android O+)
    // --------------------------------------------------------------------
    private void ensureChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm.getNotificationChannel(PermisosHelper.CHANNEL_ID) == null) {
                NotificationChannel ch = new NotificationChannel(PermisosHelper.CHANNEL_ID, "Escaneo de Beacons", NotificationManager.IMPORTANCE_LOW);
                nm.createNotificationChannel(ch);
            }
        }
    }

    // --------------------------------------------------------------------
    // Envía broadcast de estado general del servicio
    // --------------------------------------------------------------------
    private void sendStatus(boolean ok, String step, String msg) {
        Intent i = new Intent("com.example.sprint1.STATUS");
        i.putExtra("ok", ok);
        i.putExtra("step", step);
        i.putExtra("msg", msg);
        sendBroadcast(i);
    }

    // --------------------------------------------------------------------
    // Indica si el servicio está corriendo
    // --------------------------------------------------------------------
    public static boolean isRunning() {
        return isRunning;
    }

    // --------------------------------------------------------------------
    // Indica si un beacon fue detectado en los últimos 5 segundos
    // --------------------------------------------------------------------
    public static boolean isBeaconDetectedRecently() {
        return isRunning && (System.currentTimeMillis() - lastDetectedTime < 5000);
    }
}
