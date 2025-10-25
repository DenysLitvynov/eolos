/**
 * Fichero: MainActivity.java
 * Descripción: Clase principal de la app Android. Se encarga de inicializar la UI, configurar
 *              el escáner de iBeacons y manejar el ciclo de permisos necesarios.
 *              También envía las medidas captadas al servidor definido.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 25/09/2025
 */

package com.example.eolos;

import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class MainActivity extends AppCompatActivity {

    private static final int CODIGO_PETICION_PERMISOS = 11223344;
    private EscanerIBeacons escaner;
    private LogicaFake logicaFake = new LogicaFake();
    private TextView tvMedidas;
    // private String urlServidor = "https://webhook.site/d839c356-4b86-4e52-b23a-6dc7b339a7c9";
    private String baseUrl = "http://192.168.1.30:8000";  // <- Solo cambia ESTO (IP + puerto).
    private String endpointGuardar = "/api/v1/guardar-medida";  // <- Endpoint específico
    private static final String ETIQUETA_LOG = ">>>>";

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvMedidas = findViewById(R.id.tv_medidas);

        escaner = new EscanerIBeacons(this, jsonMedida -> {
            runOnUiThread(() -> {
                tvMedidas.setText("Última medida recibida: " + jsonMedida);
                Toast.makeText(this, "Enviando a servidor...", Toast.LENGTH_SHORT).show();
            });
            // logicaFake.guardarMedida(jsonMedida, urlServidor);
            logicaFake.guardarMedida(jsonMedida, baseUrl, endpointGuardar);
        });

        Log.d(ETIQUETA_LOG, " onCreate(): empieza ");

        escaner.inicializarBlueTooth();

        Log.d(ETIQUETA_LOG, " onCreate(): termina ");

        escaner.iniciarEscaneoAutomatico("EmisoraBLE");
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    /**
     * Callback invocado tras la solicitud de permisos en tiempo de ejecución.
     * Verifica si el usuario concedió los permisos necesarios y, de ser así,
     * reinicia el escaneo automático de iBeacons.
     *
     * @param requestCode int - Código de la petición realizada (para distinguir múltiples solicitudes).
     * @param permissions String[] - Lista de permisos solicitados.
     * @param grantResults int[] - Resultados de cada permiso (concedido o denegado).
     */
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                           int[] grantResults) {
        super.onRequestPermissionsResult( requestCode, permissions, grantResults);

        switch (requestCode) {
            case CODIGO_PETICION_PERMISOS:
                if (grantResults.length > 0 &&
                        grantResults[0] == PackageManager.PERMISSION_GRANTED) {

                    Log.d(ETIQUETA_LOG, " onRequestPermissionResult(): permisos concedidos  !!!!");
                    escaner.iniciarEscaneoAutomatico("ProbaEnCasa");
                }  else {

                    Log.d(ETIQUETA_LOG, " onRequestPermissionResult(): Socorro: permisos NO concedidos  !!!!");

                }
                return;
        }
    } // ()
} // class

// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------