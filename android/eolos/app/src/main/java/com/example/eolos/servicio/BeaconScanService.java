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
import com.example.eolos.logica_fake.LogicaTrayectosFake;

public class BeaconScanService extends Service {

    private EscanerIBeacons escanerIBeacons;
    private LogicaTrayectosFake logicaTrayectos;
    private static final String TAG = "BeaconSvc";
    private static final String ACTION_STOP = "ACTION_STOP_BEACON_SCAN";
    private static final int NOTIF_ID = 1;
    private static boolean isRunning = false;

    private static long lastDetectedTime = 0;

    @Override
    public void onCreate() {
        super.onCreate();
        ensureChannel();
        // Usar Singleton
        logicaTrayectos = LogicaTrayectosFake.getInstance(this);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 1. DETENER SERVICIO
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            Log.i(TAG, "Deteniendo servicio por orden explícita");
            detenerEscaneo();
            return START_NOT_STICKY;
        }

        // 2. Notificación obligatoria (foreground)
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 100, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notif = new NotificationCompat.Builder(this, PermisosHelper.CHANNEL_ID)
                .setContentTitle("Escaneando beacon...")
                .setContentText("Buscando el dispositivo conectado por QR")
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)
                .setContentIntent(pi)
                .build();

        startForeground(NOTIF_ID, notif);

        // 3. Si ya está corriendo → no hacemos nada más
        if (isRunning) {
            Log.i(TAG, "Servicio ya estaba en ejecución");
            return START_STICKY;
        }

        // 4. VALIDAR PARÁMETROS OBLIGATORIOS
        if (intent == null || intent.getStringExtra("beacon_uuid") == null) {
            Log.e(TAG, "Falta el parámetro 'beacon_uuid'. Deteniendo servicio.");
            stopSelf();
            return START_NOT_STICKY;
        }

        String uuid = intent.getStringExtra("beacon_uuid").trim();
        if (uuid.isEmpty()) {
            Log.e(TAG, "beacon_uuid vacío. Deteniendo servicio.");
            stopSelf();
            return START_NOT_STICKY;
        }

        String idBici = intent.getStringExtra("id_bici");

        // 5. INICIAR ESCANEO
        isRunning = true;
        Log.i(TAG, ">>> INICIANDO ESCANEO DEL UUID: " + uuid + " <<<");

        escanerIBeacons = EscanerIBeacons.getInstance(this, json -> {
            long ahora = System.currentTimeMillis();

            // Enviamos solo una medida cada 10 segundos como máximo
            if (ahora - lastDetectedTime >= 10_000) {
                lastDetectedTime = ahora;

                Log.i(TAG, "MEDIDA ENVIADA (cada 10s): " + json);

                // Broadcast local para quien esté escuchando
                Intent broadcast = new Intent("com.example.eolos.BEACON_DETECTED");
                broadcast.putExtra("json_medida", json);
                LocalBroadcastManager.getInstance(this).sendBroadcast(broadcast);

                // VERIFICAR que el trayecto está activo antes de guardar
                if (logicaTrayectos.estaActivo()) {
                    logicaTrayectos.guardarMedidaDesdeBeacon(json);
                    Log.i(TAG, "✅ Medida enviada a LogicaTrayectosFake");
                } else {
                    Log.w(TAG, "⚠️ Trayecto no activo, medida ignorada");
                }

                sendStatus(true, "BEACON", json);
            }
        });

        // Pasamos el id de la bici al escáner
        escanerIBeacons.setIdBici(idBici);

        // ¡Aquí empieza el escaneo real!
        escanerIBeacons.iniciarEscaneoAutomatico(uuid);

        return START_STICKY;
    }

    private void detenerEscaneo() {
        if (escanerIBeacons != null) {
            escanerIBeacons.destroy();
            escanerIBeacons = null;
        }
        stopForeground(true);
        stopSelf();
        isRunning = false;
        Log.i(TAG, "Servicio detenido correctamente");
    }

    @Override
    public void onDestroy() {
        detenerEscaneo();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void ensureChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm.getNotificationChannel(PermisosHelper.CHANNEL_ID) == null) {
                NotificationChannel channel = new NotificationChannel(
                        PermisosHelper.CHANNEL_ID,
                        "Escaneo de Beacons",
                        NotificationManager.IMPORTANCE_LOW);
                nm.createNotificationChannel(channel);
            }
        }
    }

    private void sendStatus(boolean ok, String step, String msg) {
        Intent i = new Intent("com.example.sprint1.STATUS");
        i.putExtra("ok", ok);
        i.putExtra("step", step);
        i.putExtra("msg", msg);
        sendBroadcast(i);
    }

    public static boolean isRunning() {
        return isRunning;
    }

    public static boolean isBeaconDetectedRecently() {
        return isRunning && (System.currentTimeMillis() - lastDetectedTime < 5000);
    }
}