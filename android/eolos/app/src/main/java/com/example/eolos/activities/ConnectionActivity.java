package com.example.eolos.activities;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import com.example.eolos.R;
import com.example.eolos.logica_fake.LogicaTrayectosFake;
import com.example.eolos.servicio.BeaconScanService;
import com.example.eolos.servicio.GpsDistanceTrackerService;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import org.json.JSONObject;

public class ConnectionActivity extends AppCompatActivity {

    private LogicaTrayectosFake logicaTrayectos;
    private static final String CHANNEL_ID = "connection_channel";
    private static final int NOTIFICATION_ID = 1001;
    private NotificationManager notificationManager;

    private final ActivityResultLauncher<Intent> qrLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(), result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    String qrResult = result.getData().getStringExtra("qr_result");
                    procesarQR(qrResult);
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conectar_desconectar);

        MaterialCardView cardConnect = findViewById(R.id.card_connect);
        MaterialCardView cardDisconnect = findViewById(R.id.card_disconnect);

        // Inicializar NotificationManager
        notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        createNotificationChannel();

        // Usar Singleton
        logicaTrayectos = LogicaTrayectosFake.getInstance(this);

        setupBottomNavigation();
        setupConnectButton();
        setupDisconnectButton();

        if (BeaconScanService.isRunning()) {
            cardConnect.setVisibility(View.GONE);
            cardDisconnect.setVisibility(View.VISIBLE);
        } else {
            cardConnect.setVisibility(View.VISIBLE);
            cardDisconnect.setVisibility(View.VISIBLE);
        }

        // Verificar token
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Estado de Conexión",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Notificaciones sobre el estado de conexión de bicicletas");
            notificationManager.createNotificationChannel(channel);
        }
    }

    private void showConnectionNotification(String bikeId, String uuid) {
        // Intent para abrir la Activity cuando se toque la notificación
        Intent intent = new Intent(this, ConnectionActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        // Intent para desconectar desde la notificación
        Intent disconnectIntent = new Intent(this, ConnectionActivity.class);
        disconnectIntent.setAction("ACTION_DISCONNECT_FROM_NOTIFICATION");
        PendingIntent disconnectPendingIntent = PendingIntent.getActivity(this, 1, disconnectIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(R.drawable.foto_ciclista) // Asegúrate de tener este icono
                .setContentTitle("🚴 Trayecto Activo")
                .setContentText("Bicicleta: " + bikeId + " conectada")
                .setStyle(new NotificationCompat.BigTextStyle()
                        .bigText("Bicicleta: " + bikeId + " conectada\n" +
                                "UUID: " + uuid + "\n" +
                                "Escaneando beacons y monitoreando GPS"))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setContentIntent(pendingIntent)
                .addAction(R.drawable.foto_ciclista, "Desconectar", disconnectPendingIntent)
                .setAutoCancel(false)
                .setOngoing(true) // Hace que la notificación sea persistente
                .setOnlyAlertOnce(true)
                .build();

        notificationManager.notify(NOTIFICATION_ID, notification);
    }

    private void showDisconnectionNotification() {
        Intent intent = new Intent(this, ConnectionActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(R.drawable.foto_ciclista)
                .setContentTitle("✅ Trayecto Finalizado")
                .setContentText("Bicicleta desconectada correctamente")
                .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                .setContentIntent(pendingIntent)
                .setAutoCancel(true)
                .setOngoing(false)
                .build();

        notificationManager.notify(NOTIFICATION_ID, notification);

        // Cancelar la notificación después de 3 segundos
        new Handler().postDelayed(() -> {
            notificationManager.cancel(NOTIFICATION_ID);
        }, 3000);
    }

    private void cancelConnectionNotification() {
        notificationManager.cancel(NOTIFICATION_ID);
    }

    private void setupBottomNavigation() {
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        iconInicio.setOnClickListener(v ->
                startActivity(new Intent(this, HomeActivity.class)));

        iconMapa.setOnClickListener(v ->
                Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());

        iconQR.setOnClickListener(v ->
                startActivity(new Intent(this, ConnectionActivity.class)));

        iconAlertas.setOnClickListener(v ->
                Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());

        iconPerfil.setOnClickListener(v ->
                startActivity(new Intent(this, PerfilActivity.class)));
    }

    private void setupConnectButton() {
        MaterialButton conectar = findViewById(R.id.btn_connect);
        conectar.setOnClickListener(v -> qrLauncher.launch(new Intent(this, QRScannerActivity.class)));
    }

    private void setupDisconnectButton() {
        MaterialButton desconectar = findViewById(R.id.btn_disconnect);
        desconectar.setOnClickListener(v -> {
            new MaterialAlertDialogBuilder(this)
                    .setTitle("Desconectar")
                    .setMessage("¿Estás seguro de que quieres finalizar el trayecto y detener el escaneo?")
                    .setPositiveButton("Sí", (dialog, which) -> {
                        desconectarTrayecto();
                    })
                    .setNegativeButton("Cancelar", null)
                    .show();
        });
    }

    private void desconectarTrayecto() {
        // Finalizar trayecto en la API
        if (logicaTrayectos.estaActivo()) {
            logicaTrayectos.finalizarTrayecto();
            Toast.makeText(this, "Finalizando trayecto...", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Deteniendo escaneo...", Toast.LENGTH_SHORT).show();
        }

        // Mostrar notificación de desconexión
        showDisconnectionNotification();

        // Detener servicio de beacon
        Intent stopIntent = new Intent(this, BeaconScanService.class);
        stopIntent.setAction("ACTION_STOP_BEACON_SCAN");
        startService(stopIntent);

        // Detener GPS distance service
        Intent stopGpsIntent = new Intent(this, GpsDistanceTrackerService.class);
        stopGpsIntent.setAction(GpsDistanceTrackerService.ACCION_DETENER);
        startService(stopGpsIntent);

        // Resetear instancia del Singleton
        LogicaTrayectosFake.resetInstance();

        Toast.makeText(this, "Trayecto finalizado y escaneo detenido", Toast.LENGTH_SHORT).show();
        finish();
    }

    private void procesarQR(String qrContent) {
        try {
            JSONObject json = new JSONObject(qrContent);
            String uuid = json.getString("uuid");
            String idBici = json.getString("id_bici");

            // INICIAR TRAYECTO EN LA API
            logicaTrayectos.iniciarTrayecto(idBici);
            Toast.makeText(this, "Iniciando trayecto para bicicleta: " + idBici, Toast.LENGTH_SHORT).show();

            // DETENER SERVICIO ANTERIOR SI EXISTE
            if (BeaconScanService.isRunning()) {
                Intent stopIntent = new Intent(this, BeaconScanService.class);
                stopIntent.setAction("ACTION_STOP_BEACON_SCAN");
                startService(stopIntent);
                new Handler().postDelayed(() -> iniciarNuevoEscaneo(uuid, idBici), 500);
            } else {
                iniciarNuevoEscaneo(uuid, idBici);
            }
        } catch (Exception e) {
            new MaterialAlertDialogBuilder(this)
                    .setTitle("Error")
                    .setMessage("QR no válido")
                    .setPositiveButton("OK", null)
                    .show();
        }
    }

    private void iniciarNuevoEscaneo(String uuid, String idBici) {
        new MaterialAlertDialogBuilder(this)
                .setTitle("Conexión iniciada")
                .setMessage("Escaneando beacon:\n\n" + uuid + "\n\nBicicleta: " + idBici + "\n\nTambién se está midiendo la distancia GPS recorrida.")
                .setPositiveButton("OK", (dialog, which) -> {
                    // === BEACON SERVICE ===
                    Intent beaconIntent = new Intent(this, BeaconScanService.class);
                    beaconIntent.putExtra("beacon_uuid", uuid);
                    beaconIntent.putExtra("id_bici", idBici);
                    ContextCompat.startForegroundService(this, beaconIntent);

                    // === GPS DISTANCE SERVICE ===
                    Intent gpsIntent = new Intent(this, GpsDistanceTrackerService.class);
                    startService(gpsIntent);

                    // Mostrar notificación de conexión
                    showConnectionNotification(idBici, uuid);

                    Log.d("GPS_DIST", "Servicio GPS iniciado desde ConnectionActivity");

                    Toast.makeText(this, "Escaneo + GPS activos", Toast.LENGTH_LONG).show();
                    finish();
                })
                .setCancelable(false)
                .show();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        // Manejar acción de desconexión desde la notificación
        if (intent != null && "ACTION_DISCONNECT_FROM_NOTIFICATION".equals(intent.getAction())) {
            desconectarTrayecto();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // No cancelar la notificación aquí para que persista incluso si la Activity se cierra
        // La notificación se cancela solo cuando el usuario desconecta explícitamente
    }
}