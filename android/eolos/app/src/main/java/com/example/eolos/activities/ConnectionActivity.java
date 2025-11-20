package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.LogicaTrayectosFake;
import com.example.eolos.servicio.BeaconScanService;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import org.json.JSONObject;

public class ConnectionActivity extends AppCompatActivity {

    private LogicaTrayectosFake logicaTrayectos;

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

        // Detener servicio de beacon
        Intent stopIntent = new Intent(this, BeaconScanService.class);
        stopIntent.setAction("ACTION_STOP_BEACON_SCAN");
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(stopIntent);
        } else {
            startService(stopIntent);
        }

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
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(stopIntent);
                } else {
                    startService(stopIntent);
                }
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
                .setMessage("Escaneando beacon:\n\n" + uuid + "\n\nBicicleta: " + idBici)
                .setPositiveButton("OK", (dialog, which) -> {
                    Intent serviceIntent = new Intent(this, BeaconScanService.class);
                    serviceIntent.putExtra("beacon_uuid", uuid);
                    serviceIntent.putExtra("id_bici", idBici);
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        startForegroundService(serviceIntent);
                    } else {
                        startService(serviceIntent);
                    }
                    Toast.makeText(this, "Escaneo en segundo plano iniciado", Toast.LENGTH_SHORT).show();
                    finish();
                })
                .setCancelable(false)
                .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // No resetear aquí automáticamente, solo cuando el usuario desconecta explícitamente
    }
}