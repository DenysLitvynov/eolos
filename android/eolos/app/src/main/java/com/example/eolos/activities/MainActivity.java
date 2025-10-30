/**
 * Fichero: MainActivity.java
 * Descripción: Clase principal de la app Android. Se encarga de inicializar la UI, configurar
 *              el escáner de iBeacons y manejar el ciclo de permisos necesarios.
 *              También envía las medidas captadas al servidor definido.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 25/09/2025
 */

package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.EscanerIBeacons;
import com.example.eolos.R;
import com.example.eolos.fragments.BeaconStatusFragment;
import com.example.eolos.logica_fake.LogicaFake;
import com.example.eolos.servicio.PermisosHelper;
import com.example.eolos.utils.EscanerSingleton;
import com.google.android.material.button.MaterialButton;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class MainActivity extends AppCompatActivity {

    private static final int CODIGO_PETICION_PERMISOS = 11223344;
    private EscanerIBeacons escaner;
    private LogicaFake logicaFake = new LogicaFake();
    private TextView tvMedidas;
    // private String urlServidor = "https://webhook.site/d839c356-4b86-4e52-b23a-6dc7b339a7c9";
    private String baseUrl = "http://192.168.1.25:8000";  // <- Solo cambia ESTO (IP + puerto).
    private String endpointGuardar = "/api/v1/guardar-medida";  // <- Endpoint específico
    private static final String ETIQUETA_LOG = ">>>>";

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Verificar si hay token
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token != null) {
            startActivity(new Intent(this, DashboardActivity.class));
            finish();
            return;
        }

        // Inicializar UI
        tvMedidas = findViewById(R.id.tv_medidas);
        MaterialButton loginButton = findViewById(R.id.loginButton);
        MaterialButton registerButton = findViewById(R.id.registerButton);

        // Configurar botones
        loginButton.setOnClickListener(v -> {
            startActivity(new Intent(this, LoginActivity.class));
        });

        registerButton.setOnClickListener(v -> {
            startActivity(new Intent(this, RegisterActivity.class));
        });
        escaner = new EscanerIBeacons(this, jsonMedida -> {
            runOnUiThread(() -> {
                tvMedidas.setText("Última medida recibida: " + jsonMedida);
                Toast.makeText(this, "Enviando a servidor...", Toast.LENGTH_SHORT).show();
            });
            // logicaFake.guardarMedida(jsonMedida, urlServidor);
            logicaFake.guardarMedida(jsonMedida, baseUrl, endpointGuardar);
            //iniciar servicio
            PermisosHelper.verificarYIniciarServicio(this);
        });

        Log.d(ETIQUETA_LOG, " onCreate(): empieza ");

        escaner.inicializarBlueTooth();

        Log.d(ETIQUETA_LOG, " onCreate(): termina ");

        escaner.iniciarEscaneoAutomatico("Grupo2PBIO");

        EscanerSingleton escanerSingleton = EscanerSingleton.getInstance();
        escanerSingleton.iniciarEscaneo(new EscanerIBeacons(this, jsonMedida -> {
            escanerSingleton.ultimaRecepcion = System.currentTimeMillis();
        }));

        getSupportFragmentManager()
                .beginTransaction()
                .replace(R.id.status_container, new BeaconStatusFragment())
                .commit();


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
    /**public void onRequestPermissionsResult(int requestCode, String[] permissions,
        *                                   int[] grantResults) {
       * super.onRequestPermissionsResult( requestCode, permissions, grantResults);

        *switch (requestCode) {
         *   case CODIGO_PETICION_PERMISOS:
          *      if (grantResults.length > 0 &&
           *             grantResults[0] == PackageManager.PERMISSION_GRANTED) {

            *        Log.d(ETIQUETA_LOG, " onRequestPermissionResult(): permisos concedidos  !!!!");
             *       escaner.iniciarEscaneoAutomatico("ProbaEnCasa");
              *  }  else {
*
 *                   Log.d(ETIQUETA_LOG, " onRequestPermissionResult(): Socorro: permisos NO concedidos  !!!!");

  *              }
   *             return;
    *    }
        @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        PermisosHelper.onRequestPermissionsResult(this, requestCode);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        PermisosHelper.onActivityResult(this, requestCode, resultCode, data);
    }
    } // ()
     */
} // class

// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
