/**
 * Autor: Hugo Belda
 * Fecha: 14/11/2025
 * Descripción:
     Activity para gestionar la conexión con sensores mediante QR.
     Incluye navegación inferior, botones de conectar/desconectar y
 */
package com.example.eolos.activities;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.servicio.BeaconScanService;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import org.json.JSONObject;

// --------------------------------------------------------------------
// --------------------------------------------------------------------
public class ConnectionActivity extends AppCompatActivity {

    // Lanzador de actividad para escaneo de QR. Recibe el resultado del QR escaneado.
    private final ActivityResultLauncher<Intent> qrLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    String qrResult = result.getData().getStringExtra("qr_result");
                    procesarQR(qrResult); // Procesa el contenido del QR
                }
            });

    // --------------------------------------------------------------------
    // Ciclo de vida onCreate: inicializa layout y componentes principales
    // --------------------------------------------------------------------
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conectar_desconectar);
        MaterialCardView cardConnect = findViewById(R.id.card_connect);
        MaterialCardView cardDisconnect = findViewById(R.id.card_disconnect);

        setupBottomNavigation(); // Configura la barra de navegación inferior
        setupConnectButton();    // Configura botón de conexión
        setupDisconnectButton(); // Configura botón de desconexión

        if (BeaconScanService.isRunning()) {
            cardConnect.setVisibility(View.GONE);
            cardDisconnect.setVisibility(View.VISIBLE);
        } else {
            cardConnect.setVisibility(View.VISIBLE);
            cardDisconnect.setVisibility(View.VISIBLE);
        }
    }

    // --------------------------------------------------------------------
    // Configura la navegación inferior con iconos y acciones
    // --------------------------------------------------------------------
    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        TextView iconInicio = (TextView) bottomNav.getChildAt(0);
        TextView iconMapa = (TextView) bottomNav.getChildAt(1);
        TextView iconQR = (TextView) bottomNav.getChildAt(2);
        TextView iconAlertas = (TextView) bottomNav.getChildAt(3);
        TextView iconPerfil = (TextView) bottomNav.getChildAt(4);

        iconInicio.setOnClickListener(v -> startActivity(new Intent(this, MainActivity.class)));
        iconMapa.setOnClickListener(v -> Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());
        iconQR.setOnClickListener(v -> startActivity(new Intent(this, ConnectionActivity.class)));
        iconAlertas.setOnClickListener(v -> Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());
        iconPerfil.setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }

    // --------------------------------------------------------------------
    // Configura botón de conexión para iniciar escaneo de QR
    // --------------------------------------------------------------------
    private void setupConnectButton() {
        MaterialButton conectar = findViewById(R.id.btn_connect);
        conectar.setOnClickListener(v -> qrLauncher.launch(new Intent(this, QRScannerActivity.class)));
    }

    // --------------------------------------------------------------------
    // Configura botón de desconexión para detener el servicio de beacon
    // --------------------------------------------------------------------
    private void setupDisconnectButton() {
        MaterialButton desconectar = findViewById(R.id.btn_disconnect);
        desconectar.setOnClickListener(v -> {
            Intent stopIntent = new Intent(this, BeaconScanService.class);
            stopIntent.setAction("ACTION_STOP_BEACON_SCAN");
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(stopIntent);
            } else {
                startService(stopIntent);
            }
            
            // Cancelar notificación
            NotificationHelper.cancel(this, 1); // 1 = NOTIF_ID de BeaconScanService
            
            Toast.makeText(this, "Escaneo detenido", Toast.LENGTH_SHORT).show();
        });
    }


    // --------------------------------------------------------------------
    // Procesa el contenido del QR recibido
    // json esperado: { "name": "nombre_beacon" }
    // Si hay un servicio de beacon activo, lo detiene antes de iniciar uno nuevo
    // --------------------------------------------------------------------
    private void procesarQR(String qrContent) {
        try {
            JSONObject json = new JSONObject(qrContent);
            String name = json.getString("name");

            // DETENER SERVICIO ANTERIOR SI EXISTE
            if (BeaconScanService.isRunning()) {
                Intent stopIntent = new Intent(this, BeaconScanService.class);
                stopIntent.setAction("ACTION_STOP_BEACON_SCAN");
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(stopIntent);
                } else {
                    startService(stopIntent);
                }
                // Espera 500ms antes de iniciar nuevo escaneo
                new Handler().postDelayed(() -> iniciarNuevoEscaneo(name), 500);
            } else {
                iniciarNuevoEscaneo(name);
            }

        } catch (Exception e) {
            // Dialogo de error si QR no válido
            new MaterialAlertDialogBuilder(this)
                    .setTitle("Error")
                    .setMessage("QR no válido")
                    .setPositiveButton("OK", null)
                    .show();
        }
    }

    // --------------------------------------------------------------------
    // Inicia un nuevo escaneo de beacon
    // Muestra un diálogo de confirmación y arranca el servicio en segundo plano
    // --------------------------------------------------------------------
    private void iniciarNuevoEscaneo(String name) {
        new MaterialAlertDialogBuilder(this)
                .setTitle("Conexión iniciada")
                .setMessage("Escaneando beacon:\n\n" + name)
                .setPositiveButton("OK", (dialog, which) -> {
                    Intent serviceIntent = new Intent(this, BeaconScanService.class);
                    serviceIntent.putExtra("beacon_name", name);
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        startForegroundService(serviceIntent);
                    } else {
                        startService(serviceIntent);
                    }
                    Toast.makeText(this, "Escaneo en segundo plano", Toast.LENGTH_SHORT).show();
                    finish();
                })
                .setCancelable(false)
                .show();
    }
}
