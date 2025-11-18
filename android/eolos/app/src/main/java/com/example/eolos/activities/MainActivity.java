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
        if (token != null) {
            startActivity(new Intent(this, HomeActivity.class));
            finish();
            return;
        }

        // === BOTONES LOGIN/REGISTER ===
        iniciarBotonoes();


    }

    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        TextView iconInicio    = (TextView) bottomNav.getChildAt(0);
        TextView iconMapa      = (TextView) bottomNav.getChildAt(1);
        TextView iconQR        = (TextView) bottomNav.getChildAt(2);
        TextView iconAlertas   = (TextView) bottomNav.getChildAt(3);
        TextView iconPerfil    = (TextView) bottomNav.getChildAt(4);

        iconInicio.setOnClickListener(v -> Toast.makeText(this, "Inicio", Toast.LENGTH_SHORT).show());
        iconMapa.setOnClickListener(v -> Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());
        iconQR.setOnClickListener(v -> startActivity(new Intent(this, ConnectionActivity.class)));
        iconAlertas.setOnClickListener(v -> Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());
        iconPerfil.setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }

    private void iniciarBotonoes() {
        MaterialButton loginButton = findViewById(R.id.loginButton);
        MaterialButton registerButton = findViewById(R.id.registerButton);

        loginButton.setOnClickListener(v -> startActivity(new Intent(this, LoginActivity.class)));
        registerButton.setOnClickListener(v -> startActivity(new Intent(this, RegisterActivity.class)));
    }
}