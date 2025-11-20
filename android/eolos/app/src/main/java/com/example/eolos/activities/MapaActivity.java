package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;

public class MapaActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mapa);

        setupBottomNavigation();

        // FLECHA ATRÁS DEL HEADER
        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
            // o simplemente: finish();
        }

    }

    // MENU INFERIOR
    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        if (bottomNav == null) return;

        ImageView iconInicio  = bottomNav.findViewById(R.id.icon1);
        ImageView iconMapa    = bottomNav.findViewById(R.id.icon2);
        ImageView iconQR      = bottomNav.findViewById(R.id.icon3);
        ImageView iconAlertas = bottomNav.findViewById(R.id.icon4);
        ImageView iconPerfil  = bottomNav.findViewById(R.id.icon5);

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
}