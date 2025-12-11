package com.example.eolos.servicio;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
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
    private NotificationManager notificationManager;
    private Handler beaconStatusHandler;
    private Runnable beaconStatusRunnable;
    private boolean beaconConnected = false;
    private static final String BEACON_CHANNEL_ID = "beacon_status_channel";
    private BroadcastReceiver medicionStateReceiver;

    @Override
    public void onCreate() {
        super.onCreate();
        ensureChannel();
        notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        beaconStatusHandler = new Handler(Looper.getMainLooper());
        // Usar Singleton
        logicaTrayectos = LogicaTrayectosFake.getInstance(this);

        // Registrar receiver para cambios de medición
        setupMedicionStateReceiver();
    }

    // ==================================================================
    // SETUP RECEIVER PARA CAMBIOS EN ESTADO DE MEDICIÓN (NUEVO)
    // ==================================================================
    private void setupMedicionStateReceiver() {
        medicionStateReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String estadoMedicion = intent.getStringExtra("estado_medicion");
                double valorMedicion = intent.getDoubleExtra("valor_medicion", 0);
                int icono = intent.getIntExtra("icono", android.R.drawable.presence_online);

                Log.i(TAG, "Broadcast recibido: Estado=" + estadoMedicion + ", Valor=" + valorMedicion);

                // Actualizar notificación con el estado de la medición
                updateMedicionNotification(estadoMedicion, valorMedicion, icono);
            }
        };

        IntentFilter filter = new IntentFilter("com.example.eolos.MEDICION_STATE_CHANGED");
        LocalBroadcastManager.getInstance(this).registerReceiver(medicionStateReceiver, filter);
        Log.d(TAG, "Receiver de estado de medición registrado");
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
        updateBeaconNotification(false, "Buscando beacon...");

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

        // Iniciar verificador de estado del beacon
        startBeaconStatusChecker();

        escanerIBeacons = EscanerIBeacons.getInstance(this, json -> {
            long ahora = System.currentTimeMillis();

            // Enviamos solo una medida cada 10 segundos como máximo
            if (ahora - lastDetectedTime >= 10_000) {
                lastDetectedTime = ahora;

                Log.i(TAG, "MEDIDA ENVIADA (cada 10s): " + json);

                // Actualizar notificación a estado conectado
                beaconConnected = true;
                updateBeaconNotification(true, "Beacon conectado");

                // Reiniciar el temporizador de desconexión
                resetBeaconStatusTimer();

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

    private void startBeaconStatusChecker() {
        beaconStatusRunnable = new Runnable() {
            @Override
            public void run() {
                // Si no se ha detectado el beacon en los últimos 15 segundos, mostrar como desconectado
                long tiempoSinDeteccion = System.currentTimeMillis() - lastDetectedTime;
                if (beaconConnected && tiempoSinDeteccion > 15000) {
                    beaconConnected = false;
                    updateBeaconNotification(false, "Beacon desconectado");
                }

                // Programar siguiente verificación en 5 segundos
                beaconStatusHandler.postDelayed(this, 5000);
            }
        };
        beaconStatusHandler.postDelayed(beaconStatusRunnable, 5000);
    }

    private void resetBeaconStatusTimer() {
        if (beaconStatusHandler != null && beaconStatusRunnable != null) {
            beaconStatusHandler.removeCallbacks(beaconStatusRunnable);
            beaconStatusHandler.postDelayed(beaconStatusRunnable, 15000);
        }
    }

    private void updateBeaconNotification(boolean connected, String statusText) {
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 100, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        String title = connected ? "🚴 Sensor de la bici Conectado" : "❌ Sensor de la bici Desconectado";
        int icon = connected ? android.R.drawable.presence_online : android.R.drawable.presence_busy;

        Notification notif = new NotificationCompat.Builder(this, BEACON_CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(statusText)
                .setSmallIcon(icon)
                .setOngoing(true)
                .setContentIntent(pi)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .setOnlyAlertOnce(true) // Solo alertar cuando cambie el estado
                .build();

        // Si es la primera vez, iniciar como foreground service
        if (!isRunning) {
            startForeground(NOTIF_ID, notif);
        } else {
            // Si ya está corriendo, solo actualizar la notificación
            notificationManager.notify(NOTIF_ID, notif);
        }
    }

    // ==================================================================
    // ACTUALIZAR NOTIFICACIÓN CON ESTADO DE MEDICIÓN (NUEVA)
    // ==================================================================
    private void updateMedicionNotification(String estadoMedicion, double valorMedicion, int iconoColor) {
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 100, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        String title = "Medición de Calidad del Aire";
        String content = "Estado: " + estadoMedicion + " (Valor: " + String.format("%.1f", valorMedicion) + ")";

        Notification notif = new NotificationCompat.Builder(this, BEACON_CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(content)
                .setSmallIcon(iconoColor)
                .setOngoing(true)
                .setContentIntent(pi)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .setOnlyAlertOnce(false)
                .setShowWhen(true)
                .build();

        notificationManager.notify(NOTIF_ID, notif);
        Log.i(TAG, "Notificación actualizada con estado: " + estadoMedicion);
    }

    private void detenerEscaneo() {
        // Detener el verificador de estado
        if (beaconStatusHandler != null && beaconStatusRunnable != null) {
            beaconStatusHandler.removeCallbacks(beaconStatusRunnable);
        }

        // Desregistrar receiver de medición (NUEVO)
        if (medicionStateReceiver != null) {
            try {
                LocalBroadcastManager.getInstance(this).unregisterReceiver(medicionStateReceiver);
                Log.d(TAG, "Receiver de medición desregistrado");
            } catch (Exception e) {
                Log.e(TAG, "Error desregistrando receiver", e);
            }
        }

        if (escanerIBeacons != null) {
            escanerIBeacons.destroy();
            escanerIBeacons = null;
        }

        // Actualizar notificación antes de detener
        updateBeaconNotification(false, "Servicio detenido");

        stopForeground(true);
        stopSelf();
        isRunning = false;
        beaconConnected = false;
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
        // Canal para el escaneo de beacons (existente)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm.getNotificationChannel(PermisosHelper.CHANNEL_ID) == null) {
                NotificationChannel channel = new NotificationChannel(
                        PermisosHelper.CHANNEL_ID,
                        "Escaneo de Beacons",
                        NotificationManager.IMPORTANCE_LOW);
                nm.createNotificationChannel(channel);
            }

            // Nuevo canal para el estado del beacon
            if (nm.getNotificationChannel(BEACON_CHANNEL_ID) == null) {
                NotificationChannel beaconChannel = new NotificationChannel(
                        BEACON_CHANNEL_ID,
                        "Estado del Beacon",
                        NotificationManager.IMPORTANCE_LOW);
                beaconChannel.setDescription("Muestra si el beacon está conectado o no");
                nm.createNotificationChannel(beaconChannel);
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

    public static boolean isBeaconConnected() {
        return isRunning && (System.currentTimeMillis() - lastDetectedTime < 15000);
    }
}