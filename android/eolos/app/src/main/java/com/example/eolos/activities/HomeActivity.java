package com.example.eolos.activities;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.servicio.GpsDistanceTrackerService;

import androidx.appcompat.app.AlertDialog;
import androidx.biometric.BiometricManager;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

public class HomeActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_page_usuario_registrado); // el que hemos ido tocando

        setupBottomNavigation();    // Configura la barra de navegación inferior

        // Verificar token
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        boolean biometricAsked = prefs.getBoolean("biometric_asked", false);
        if (!biometricAsked) {
            BiometricManager biometricManager = BiometricManager.from(this);
            int canAuth = biometricManager.canAuthenticate(
                    BiometricManager.Authenticators.BIOMETRIC_STRONG
            );

            if (canAuth == BiometricManager.BIOMETRIC_SUCCESS) {
                new AlertDialog.Builder(this)
                        .setTitle(getString(R.string.biometric_enable_title))
                        .setMessage(getString(R.string.biometric_enable_message))
                        .setPositiveButton("Sí", (dialog, which) -> {
                            prefs.edit()
                                    .putBoolean("biometric_enabled", true)
                                    .putBoolean("biometric_asked", true)
                                    .apply();
                            Toast.makeText(HomeActivity.this,
                                    "Inicio con huella activado",
                                    Toast.LENGTH_SHORT).show();

                            // ⭐ NUEVO: fijar dueño solo si aún no hay ninguno
                            SharedPreferences authPrefs = getSharedPreferences("auth", MODE_PRIVATE);
                            String existingOwner = authPrefs.getString("biometric_owner_email", null);
                            if (existingOwner == null) {
                                String email = authPrefs.getString("biometric_email", null);
                                String tokenActual = authPrefs.getString("token", null);
                                if (email != null && tokenActual != null) {
                                    authPrefs.edit()
                                            .putString("biometric_owner_email", email)
                                            .putString("biometric_owner_token", tokenActual)
                                            .apply();
                                }
                            }

                        })
                        .setNegativeButton("Ahora no", (dialog, which) -> {
                            prefs.edit()
                                    .putBoolean("biometric_asked", true)
                                    .apply();
                        })
                        .show();
            } else {
                // No hay biometría disponible: marcamos como preguntado para no molestar más
                prefs.edit().putBoolean("biometric_asked", true).apply();
            }
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
                startActivity(new Intent(this, MapaActivity.class)));

        iconQR.setOnClickListener(v ->
                startActivity(new Intent(this, ConnectionActivity.class)));

        iconAlertas.setOnClickListener(v ->
                startActivity(new Intent(this, IncidenciaActivity.class)));


        iconPerfil.setOnClickListener(v ->
                startActivity(new Intent(this, PerfilActivity.class)));
    }

    //------------------------------------------------------------------------------------------
    //  void  →  void
    //  setupDistanceLiveTracking() – VERSIÓN FINAL 100% FUNCIONAL
    //------------------------------------------------------------------------------------------
    private final BroadcastReceiver distanceReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            Log.d("GPS_DIST", "BROADCAST RECIBIDO en Home → " + action);

            View contenedor = findViewById(R.id.contenedor_trayecto_actual);
            TextView tv = findViewById(R.id.tv_distancia_actual);

            if (contenedor == null || tv == null) {
                Log.e("GPS_DIST", "ERROR: Views no encontradas!");
                return;
            }

            if (GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA.equals(action)) {
                float metros = intent.getFloatExtra(GpsDistanceTrackerService.EXTRA_DISTANCIA, 0f);
                Log.d("GPS_DIST", "Distancia actualizada: " + metros + " metros");

                contenedor.setVisibility(View.VISIBLE);
                tv.setText(metros >= 1000
                        ? String.format("%.2f km", metros / 1000f)
                        : String.format("%.1f m", metros));
            }
            else if (GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO.equals(action)) {
                Log.d("GPS_DIST", "Servicio GPS detenido");
                contenedor.setVisibility(View.GONE);
                tv.setText("0.0 m");
            }
        }
    };

    private void iniciarSeguiminetoDistancia() {
        // Verificar estado actual del servicio al iniciar la actividad
        if (GpsDistanceTrackerService.isRunning()) {
            View contenedor = findViewById(R.id.contenedor_trayecto_actual);
            if (contenedor != null) {
                contenedor.setVisibility(View.VISIBLE);
            }
            Log.d("GPS_DIST", "Servicio GPS está corriendo al iniciar Home");
        } else {
            Log.d("GPS_DIST", "Servicio GPS NO está corriendo al iniciar Home");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        IntentFilter filter = new IntentFilter();
        filter.addAction(GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA);
        filter.addAction(GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO);
        LocalBroadcastManager.getInstance(this).registerReceiver(distanceReceiver, filter);

        Log.d("GPS_DIST", "Receiver registrado correctamente");
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(distanceReceiver);
        } catch (Exception ignored) {}
        Log.d("GPS_DIST", "Receiver desregistrado");
    }

}