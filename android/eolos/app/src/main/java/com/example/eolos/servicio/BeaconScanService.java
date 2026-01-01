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

    // IDs de notificación (cada una con su función, sin pisarse)
    private static final int NOTIF_ID_FOREGROUND = 1;   // Notificación del servicio foreground (estado beacon)
    private static final int NOTIF_ID_AIR_ALERT = 2;    // Alerta alta prioridad (solo cuando hay riesgo)
    private static final int NOTIF_ID_MEASUREMENT = 3;  // Notificación persistente de medición (silenciosa)

    private static boolean isRunning = false;
    private static long lastDetectedTime = 0;

    private NotificationManager notificationManager;
    private Handler beaconStatusHandler;
    private Runnable beaconStatusRunnable;
    private boolean beaconConnected = false;

    // Canales de notificación
    private static final String BEACON_CHANNEL_ID = "beacon_status_channel"; // baja prioridad (persistente)
    private static final String AIR_ALERT_CHANNEL_ID = "air_alert_channel"; // alta prioridad (alertas)

    private BroadcastReceiver medicionStateReceiver;

    // Umbral numérico para mostrar alerta (además del texto del estado)
    private static final double ALERT_THRESHOLD_VALUE = 100.0;

    // Para que sonido/vibración ocurra SOLO al entrar en alerta
    private boolean alertActive = false;

    @Override
    public void onCreate() {
        super.onCreate();

        ensureChannels();

        notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        beaconStatusHandler = new Handler(Looper.getMainLooper());

        logicaTrayectos = LogicaTrayectosFake.getInstance(this);

        setupMedicionStateReceiver();
    }

    // =====================================================================
    // Receiver: recibe cambios de estado de medición desde LogicaTrayectosFake
    // =====================================================================
    private void setupMedicionStateReceiver() {
        medicionStateReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {

                String estadoMedicion = intent.getStringExtra("estado_medicion");
                double valorMedicion = intent.getDoubleExtra("valor_medicion", 0);

                // ✅ Este tipo viene como String: "pm2_5", "pm10", "co2", "no2"...
                String tipo = intent.getStringExtra("tipo_medicion");

                // Icono: debe ser un drawable id (no color)
                int iconResId = intent.getIntExtra("icono", android.R.drawable.presence_online);

                Log.i(TAG, "MEDICION_STATE_CHANGED: tipo=" + tipo
                        + ", estado=" + estadoMedicion
                        + ", valor=" + valorMedicion);

                // 1) Notificación persistente (silenciosa) con estado actual de medición
                updateMedicionNotification(tipo, estadoMedicion, valorMedicion, iconResId);

                // 2) Alerta: si hay riesgo -> mostrar/actualizar; si no -> cancelar
                if (shouldAlert(tipo, estadoMedicion, valorMedicion)) {
                    showOrUpdateAirQualityAlert(tipo);
                } else {
                    notificationManager.cancel(NOTIF_ID_AIR_ALERT);
                    alertActive = false; // vuelve a permitir sonido cuando entre de nuevo en alerta
                }
            }
        };

        IntentFilter filter = new IntentFilter("com.example.eolos.MEDICION_STATE_CHANGED");
        LocalBroadcastManager.getInstance(this).registerReceiver(medicionStateReceiver, filter);
        Log.d(TAG, "Receiver MEDICION_STATE_CHANGED registrado");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        // 1) Detener servicio si llega la acción de stop
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            Log.i(TAG, "Deteniendo servicio por ACTION_STOP");
            detenerEscaneo();
            return START_NOT_STICKY;
        }

        // 2) Notificación obligatoria para foreground service
        updateBeaconNotification(false, "Buscando beacon...");

        // 3) Si ya está corriendo, no reiniciar
        if (isRunning) {
            Log.i(TAG, "Servicio ya estaba en ejecución");
            return START_STICKY;
        }

        // 4) Validar parámetros
        if (intent == null || intent.getStringExtra("beacon_uuid") == null) {
            Log.e(TAG, "Falta 'beacon_uuid'. Deteniendo servicio.");
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

        // 5) Iniciar escaneo
        isRunning = true;
        Log.i(TAG, ">>> INICIANDO ESCANEO UUID: " + uuid + " <<<");

        startBeaconStatusChecker();

        escanerIBeacons = EscanerIBeacons.getInstance(this, json -> {
            long ahora = System.currentTimeMillis();

            // Para no saturar: máximo una medida cada 10 segundos
            if (ahora - lastDetectedTime >= 10_000) {
                lastDetectedTime = ahora;

                Log.i(TAG, "MEDIDA ENVIADA (cada 10s): " + json);

                beaconConnected = true;
                updateBeaconNotification(true, "Beacon conectado");
                resetBeaconStatusTimer();

                // Broadcast local para UI
                Intent broadcast = new Intent("com.example.eolos.BEACON_DETECTED");
                broadcast.putExtra("json_medida", json);
                LocalBroadcastManager.getInstance(this).sendBroadcast(broadcast);

                // Guardar medida -> Logica enviará MEDICION_STATE_CHANGED
                if (logicaTrayectos.estaActivo()) {
                    logicaTrayectos.guardarMedidaDesdeBeacon(json);
                    Log.i(TAG, "✅ Medida enviada a LogicaTrayectosFake");
                } else {
                    Log.w(TAG, "⚠️ Trayecto no activo, medida ignorada");
                }
            }
        });

        escanerIBeacons.setIdBici(idBici);
        escanerIBeacons.iniciarEscaneoAutomatico(uuid);

        return START_STICKY;
    }

    // =====================================================================
    // Verificador: si no se detecta beacon en 15s -> desconectado
    // =====================================================================
    private void startBeaconStatusChecker() {
        beaconStatusRunnable = new Runnable() {
            @Override
            public void run() {
                long tiempoSinDeteccion = System.currentTimeMillis() - lastDetectedTime;
                if (beaconConnected && tiempoSinDeteccion > 15000) {
                    beaconConnected = false;
                    updateBeaconNotification(false, "Beacon desconectado");
                }
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

    // =====================================================================
    // Notificación foreground: estado del beacon (persistente, baja prioridad)
    // =====================================================================
    private void updateBeaconNotification(boolean connected, String statusText) {
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(
                this, 100, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String title = connected ? "🚴 Sensor de la bici Conectado" : "❌ Sensor de la bici Desconectado";
        int icon = connected ? android.R.drawable.presence_online : android.R.drawable.presence_busy;

        Notification notif = new NotificationCompat.Builder(this, BEACON_CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(statusText)
                .setSmallIcon(icon)
                .setOngoing(true)
                .setContentIntent(pi)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .setOnlyAlertOnce(true)
                .build();

        if (!isRunning) {
            startForeground(NOTIF_ID_FOREGROUND, notif);
        } else {
            notificationManager.notify(NOTIF_ID_FOREGROUND, notif);
        }
    }

    // =====================================================================
    // Notificación persistente: estado de medición (silenciosa)
    // =====================================================================
    private void updateMedicionNotification(String tipo, String estadoMedicion, double valorMedicion, int iconResId) {
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(
                this, 101, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String pollutant = formatTipoForUi(tipo);

        String title = "Medición de Calidad del Aire";
        String content = pollutant + " · Estado: " + safe(estadoMedicion)
                + " (Valor: " + String.format("%.1f", valorMedicion) + ")";

        Notification notif = new NotificationCompat.Builder(this, BEACON_CHANNEL_ID)
                .setContentTitle(title)
                .setContentText(content)
                .setSmallIcon(iconResId)
                .setOngoing(true)
                .setContentIntent(pi)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .setOnlyAlertOnce(true)
                .setShowWhen(true)
                .build();

        // ✅ Nota: usamos un ID distinto para no pisar la notificación foreground del servicio
        notificationManager.notify(NOTIF_ID_MEASUREMENT, notif);
    }

    // =====================================================================
    // Decide si hay que mostrar alerta (por estado de texto o por umbral numérico)
    // =====================================================================
    private boolean shouldAlert(String tipo, String estadoMedicion, double valorMedicion) {
        if (estadoMedicion != null) {
            String s = estadoMedicion.trim().toLowerCase();
            if (s.contains("mala") || s.contains("muy mala") || s.contains("pelig")) {
                return true;
            }
        }
        return valorMedicion >= ALERT_THRESHOLD_VALUE;
    }

    // =====================================================================
    // Alerta: alta prioridad (formato tipo Figma)
    // - Suena SOLO al entrar en alerta
    // - Si sigue en alerta, se actualiza el texto sin volver a molestar
    // =====================================================================
    private void showOrUpdateAirQualityAlert(String tipo) {
        Intent openApp = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(
                this, 200, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String pollutant = formatTipoForUi(tipo);

        String title = "Alerta!";
        String text = "Altos niveles de " + pollutant + " detectados en la zona.";

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, AIR_ALERT_CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle(title)
                .setContentText(text)
                .setContentIntent(pi)
                .setAutoCancel(true)
                .setPriority(NotificationCompat.PRIORITY_HIGH);

        // Solo la primera vez que entra en alerta: sonido/vibración
        if (!alertActive) {
            builder.setDefaults(NotificationCompat.DEFAULT_ALL);
            alertActive = true;
        } else {
            builder.setOnlyAlertOnce(true);
        }

        notificationManager.notify(NOTIF_ID_AIR_ALERT, builder.build());
    }

    // Convierte tipo interno ("co2", "pm10"...) a texto UI ("CO₂", "PM10"...)
    private String formatTipoForUi(String tipo) {
        if (tipo == null) return "contaminante";

        String t = tipo.trim().toLowerCase();
        switch (t) {
            case "pm2_5":
            case "pm2.5":
                return "PM2.5";
            case "pm10":
                return "PM10";
            case "co2":
                return "CO₂";
            case "no2":
                return "NO₂";
            default:
                return tipo.toUpperCase();
        }
    }

    private String safe(String s) {
        return (s == null || s.trim().isEmpty()) ? "-" : s.trim();
    }

    // =====================================================================
    // Detener escaneo y limpiar recursos
    // =====================================================================
    private void detenerEscaneo() {
        if (beaconStatusHandler != null && beaconStatusRunnable != null) {
            beaconStatusHandler.removeCallbacks(beaconStatusRunnable);
        }

        if (medicionStateReceiver != null) {
            try {
                LocalBroadcastManager.getInstance(this).unregisterReceiver(medicionStateReceiver);
            } catch (Exception e) {
                Log.e(TAG, "Error desregistrando receiver", e);
            }
        }

        if (escanerIBeacons != null) {
            escanerIBeacons.destroy();
            escanerIBeacons = null;
        }

        // Cancelar también la notificación de medición y la alerta
        notificationManager.cancel(NOTIF_ID_MEASUREMENT);
        notificationManager.cancel(NOTIF_ID_AIR_ALERT);
        alertActive = false;

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

    // =====================================================================
    // Canales de notificación (Android O+)
    // =====================================================================
    private void ensureChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

            if (nm.getNotificationChannel(BEACON_CHANNEL_ID) == null) {
                NotificationChannel beaconChannel = new NotificationChannel(
                        BEACON_CHANNEL_ID,
                        "Estado del Beacon",
                        NotificationManager.IMPORTANCE_LOW
                );
                beaconChannel.setDescription("Estado de conexión y estado de medición");
                nm.createNotificationChannel(beaconChannel);
            }

            if (nm.getNotificationChannel(AIR_ALERT_CHANNEL_ID) == null) {
                NotificationChannel alertChannel = new NotificationChannel(
                        AIR_ALERT_CHANNEL_ID,
                        "Alertas de Calidad del Aire",
                        NotificationManager.IMPORTANCE_HIGH
                );
                alertChannel.setDescription("Alertas cuando la calidad del aire sea mala o muy alta");
                nm.createNotificationChannel(alertChannel);
            }
        }
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
