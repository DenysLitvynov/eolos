/**
 * Autor: Hugo Belda
 * Fecha: 14/11/2025
 * Descripción: Activity encargada de escanear códigos QR utilizando la librería ZXing.
 *             Integra CaptureManager para gestionar automáticamente el ciclo de vida del escáner,
 *             muestra la vista de cámara y devuelve el contenido del QR a la actividad que la lanzó
 *             (ConnectionActivity) mediante setResult(). Incluye barra de navegación inferior.
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

    private CaptureManager capture;              // Controla el ciclo de vida del escaneo
    private DecoratedBarcodeView barcodeScannerView; // Vista de cámara para escaneo QR

    /**
     * @param savedInstanceState Estado previamente guardado de la actividad (puede ser null)
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qr_scan);

        // === VISTA DE ESCANEO ===
        barcodeScannerView = findViewById(R.id.zxing_barcode_scanner);
        capture = new CaptureManager(this, barcodeScannerView);
        capture.initializeFromIntent(getIntent(), savedInstanceState);
        capture.decode(); // Inicia el escaneo automático;
    }

    /**
     * Se llama cuando la actividad vuelve a estar visible.
     * Delega la reanudación del escáner a CaptureManager.
     */
    @Override
    protected void onResume() {
        super.onResume();
        capture.onResume();
    }

    /**
     * Se llama cuando la actividad pierde el foco.
     * Delega la pausa del escáner a CaptureManager.
     */
    @Override
    protected void onPause() {
        super.onPause();
        capture.onPause();
    }

    /**
     * Se llama cuando la actividad va a ser destruida.
     * Delega la limpieza del escáner a CaptureManager.
     */
    @Override
    protected void onDestroy() {
        super.onDestroy();
        capture.onDestroy();
    }

    /**
     * @param outState Bundle donde guardar el estado de la actividad
     */
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        capture.onSaveInstanceState(outState); // Guardar estado de escaneo
    }

    /**
     * @param requestCode  Código de solicitud de permiso
     * @param permissions  Array con los permisos solicitados
     * @param grantResults Array con los resultados de los permisos
     */
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        capture.onRequestPermissionsResult(requestCode, permissions, grantResults); // Delegar permisos
    }

    /**
     * @param savedInstanceState Estado previamente guardado (puede ser null)
     * Configura el escaneo continuo: cuando se detecta un QR, pausa el escáner,
     * muestra el contenido y devuelve el resultado a la actividad llamadora.
     */
    @Override
    protected void onPostCreate(Bundle savedInstanceState) {
        super.onPostCreate(savedInstanceState);
        barcodeScannerView.decodeContinuous(result -> {
            barcodeScannerView.pause(); // Pausar para evitar múltiples lecturas
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