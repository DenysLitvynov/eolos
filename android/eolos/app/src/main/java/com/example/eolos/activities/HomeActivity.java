package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;

import androidx.appcompat.app.AlertDialog;
import androidx.biometric.BiometricManager;

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

}