/**
 * Fichero: MainActivity.java
 * Descripción: Pantalla principal de login/register. NO inicia escáner.
 * @author Denys Litvynov Lymanets
 * @version 2.0
 * @since 25/09/2025
 */

package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.fragments.BeaconStatusFragment;
import com.example.eolos.servicio.PermisosHelper;
import com.google.android.material.button.MaterialButton;

// --------------------------------------------------------------------
// --------------------------------------------------------------------
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // === MENÚ DE NAVEGACIÓN INFERIOR ===
        //setupBottomNavigation();

        // === Verificar permisos ===
        PermisosHelper.verificarYIniciarServicio(this);

        // === REDIRECCIÓN SI YA ESTÁ LOGUEADO ===
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        boolean biometricEnabled = prefs.getBoolean("biometric_enabled", false);
        if (token != null && biometricEnabled) {
            startActivity(new Intent(this, HomeActivity.class));
            finish();
            return;
        }

        // === BOTONES LOGIN/REGISTER ===
        iniciarBotonoes();

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

    private void iniciarBotonoes() {
        MaterialButton loginButton = findViewById(R.id.loginButton);
        MaterialButton registerButton = findViewById(R.id.registerButton);

        loginButton.setOnClickListener(v -> startActivity(new Intent(this, LoginActivity.class)));
        registerButton.setOnClickListener(v -> startActivity(new Intent(this, RegisterActivity.class)));
    }
}