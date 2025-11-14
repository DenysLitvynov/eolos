/**
 * Autor: Hugo Belda
 * Fecha: 14/11/2025
 * Descripción:
 */

package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.journeyapps.barcodescanner.CaptureManager;
import com.journeyapps.barcodescanner.DecoratedBarcodeView;

// --------------------------------------------------------------------
// --------------------------------------------------------------------
public class QRScannerActivity extends AppCompatActivity {

    private CaptureManager capture;                // Controla el ciclo de vida del escaneo
    private DecoratedBarcodeView barcodeScannerView; // Vista de cámara para escaneo QR

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qr_scan);


        // === VISTA DE ESCANEO ===
        barcodeScannerView = findViewById(R.id.zxing_barcode_scanner);
        capture = new CaptureManager(this, barcodeScannerView);
        capture.initializeFromIntent(getIntent(), savedInstanceState);
        capture.decode();  // Inicia el escaneo automático;

        // === MENÚ DE NAVEGACIÓN INFERIOR ===
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);

        // Obtener cada ícono por posición (getChildAt)
        TextView iconInicio = (TextView) bottomNav.getChildAt(0);
        TextView iconMapa = (TextView) bottomNav.getChildAt(1);
        TextView iconQR = (TextView) bottomNav.getChildAt(2);
        TextView iconAlertas = (TextView) bottomNav.getChildAt(3);
        TextView iconPerfil = (TextView) bottomNav.getChildAt(4);

        // Configurar clics
        iconInicio.setOnClickListener(v -> Toast.makeText(this, "Inicio", Toast.LENGTH_SHORT).show());

        iconMapa.setOnClickListener(v -> Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());

        iconQR.setOnClickListener(v -> {
            startActivity(new Intent(this, ConnectionActivity.class));
        });

        iconAlertas.setOnClickListener(v -> Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());

        iconPerfil.setOnClickListener(v -> {
            startActivity(new Intent(this, PerfilActivity.class));
        });
    }

    // --------------------------------------------------------------------
    // CICLO DE VIDA: delegar control del escaneo a CaptureManager
    // --------------------------------------------------------------------
    @Override
    protected void onResume() {
        super.onResume();
        capture.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        capture.onPause();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        capture.onDestroy();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        capture.onSaveInstanceState(outState); // Guardar estado de escaneo
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        capture.onRequestPermissionsResult(requestCode, permissions, grantResults); // Delegar permisos
    }

    // --------------------------------------------------------------------
    // ESCANEO CONTINUO: actualizar estado y devolver resultado
    // --------------------------------------------------------------------
    @Override
    protected void onPostCreate(Bundle savedInstanceState) {
        super.onPostCreate(savedInstanceState);

        barcodeScannerView.decodeContinuous(result -> {
            barcodeScannerView.pause();           // Pausar para evitar múltiples lecturas
            String qrContent = result.getText();

            // Mostrar contenido por Toast
            Toast.makeText(this, "QR Escaneado: " + qrContent, Toast.LENGTH_LONG).show();

            // Devolver resultado a la actividad que inició el escaneo
            Intent data = new Intent();
            data.putExtra("qr_result", qrContent);
            setResult(RESULT_OK, data);

            finish(); // Cierra la actividad de escaneo
        });
    }
}