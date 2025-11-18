/**
 * Autor: Hugo Belda
 * Fecha: 14/11/2025
 * Descripción: Activity para gestionar la conexión con sensores mediante QR. Incluye navegación inferior,
 *             botones de conectar/desconectar y gestión del servicio de escaneo de beacons en segundo plano.
 *             Permite escanear un código QR que contiene el nombre del beacon, detener un escaneo anterior
 *             si lo hubiera, e iniciar uno nuevo mostrando confirmación al usuario.
 */
package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.ImageView;
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
            new ActivityResultContracts.StartActivityForResult(), result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    String qrResult = result.getData().getStringExtra("qr_result");
                    procesarQR(qrResult); // Procesa el contenido del QR
                }
            });

    // --------------------------------------------------------------------
    // Ciclo de vida onCreate: inicializa layout y componentes principales
    // --------------------------------------------------------------------
    /**
     * @param savedInstanceState Estado previamente guardado de la actividad (puede ser null)
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conectar_desconectar);

        MaterialCardView cardConnect = findViewById(R.id.card_connect);
        MaterialCardView cardDisconnect = findViewById(R.id.card_disconnect);

        setupBottomNavigation();    // Configura la barra de navegación inferior
        setupConnectButton();       // Configura botón de conexión
        setupDisconnectButton();    // Configura botón de desconexión

        if (BeaconScanService.isRunning()) {
            cardConnect.setVisibility(View.GONE);
            cardDisconnect.setVisibility(View.VISIBLE);
        } else {
            cardConnect.setVisibility(View.VISIBLE);
            cardDisconnect.setVisibility(View.VISIBLE);
        }


        // SI AIXOOO EU BORREM
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

    // --------------------------------------------------------------------
    // Configura la navegación inferior con iconos y acciones
    // --------------------------------------------------------------------
    /**
     * Configura los listeners de la barra de navegación inferior.
     * No recibe parámetros ni devuelve nada.
     */

    private void setupBottomNavigation() {

        // Recuperamos cada icono directamente por su ID real del XML
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        // Listeners según tu lógica original
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


    // --------------------------------------------------------------------
    // Configura botón de conexión para iniciar escaneo de QR
    // --------------------------------------------------------------------
    /**
     * Configura el botón "Conectar" para lanzar la actividad de escaneo QR.
     * No recibe parámetros ni devuelve nada.
     */
    private void setupConnectButton() {
        MaterialButton conectar = findViewById(R.id.btn_connect);
        conectar.setOnClickListener(v -> qrLauncher.launch(new Intent(this, QRScannerActivity.class)));
    }

    // --------------------------------------------------------------------
    // Configura botón de desconexión para detener el servicio de beacon
    // --------------------------------------------------------------------
    /**
     * Configura el botón "Desconectar" para detener el servicio de escaneo de beacons.
     * No recibe parámetros ni devuelve nada.
     */
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
            // Mostrar notificación visual al usuario
            Toast.makeText(this, "Escaneo detenido", Toast.LENGTH_SHORT).show();
        });
    }

    // --------------------------------------------------------------------
    // Procesa el contenido del QR recibido
    // json esperado: { "name": "nombre_beacon" }
    // Si hay un servicio de beacon activo, lo detiene antes de iniciar uno nuevo
    // --------------------------------------------------------------------
    /**
     * @param qrContent Contenido en formato JSON del código QR escaneado
     */
    private void procesarQR(String qrContent) {
        try {
            JSONObject json = new JSONObject(qrContent);
            String name = json.getString("name");

            // DETENER SERVicio ANTERIOR SI EXISTE
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
    /**
     * @param name Nombre del beacon obtenido del QR
     */
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