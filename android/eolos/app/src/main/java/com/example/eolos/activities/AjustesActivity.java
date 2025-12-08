package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.google.android.material.button.MaterialButton;

public class AjustesActivity extends AppCompatActivity {

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

    private MaterialButton btnLogout;
    private MaterialButton btnDeleteAccount;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ajustes);


        setupBottomNavigation();

        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
        }
        // SharedPreferences
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);

        // Si NO hay token, redirige a Login (igual que en PerfilActivity)
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        // --- Botones de sesión / cuenta ---
        btnLogout = findViewById(R.id.logoutButton);

        if (btnLogout != null) {
            btnLogout.setOnClickListener(v -> {
                prefs.edit()
                        .remove("token")
                        .remove("targeta_id")
                        .apply();
                Toast.makeText(this, "Sesión cerrada", Toast.LENGTH_SHORT).show();
                startActivity(new Intent(this, MainActivity.class));
                finish();
            });
        }

        // --- Política de privacidad ---
        FrameLayout seccionPolitica = findViewById(R.id.seccion_politica_privacidad);
        TextView textoPolitica = findViewById(R.id.tv_texto_politica);
        ImageView iconPolitica = findViewById(R.id.icon_politica);

// --- Términos y condiciones ---
        FrameLayout seccionTerminos = findViewById(R.id.seccion_terminos);
        TextView textoTerminos = findViewById(R.id.tv_texto_terminos);
        ImageView iconTerminos = findViewById(R.id.icon_terminos);

// --- FAQs ---
        FrameLayout seccionFaqs = findViewById(R.id.seccion_faqs);
        LinearLayout contenedorFaqs = findViewById(R.id.contenedor_faqs);
        ImageView iconFaqs = findViewById(R.id.icon_faqs);

// Listener genérico para secciones plegables
        setupExpandableSection(seccionPolitica, textoPolitica, iconPolitica);
        setupExpandableSection(seccionTerminos, textoTerminos, iconTerminos);
        setupExpandableSection(seccionFaqs, contenedorFaqs, iconFaqs);
    }

    private void setupExpandableSection(View clickable, final View contenido, final ImageView icon) {
        if (clickable == null || contenido == null) return;

        View.OnClickListener listener = v -> {
            boolean isVisible = contenido.getVisibility() == View.VISIBLE;
            contenido.setVisibility(isVisible ? View.GONE : View.VISIBLE);

            if (icon != null) {
                icon.setImageResource(
                        isVisible ? R.drawable.ic_chevron_right : R.drawable.ic_chevron_down
                );
            }
        };

        // Hacemos clicable todo el bloque
        clickable.setOnClickListener(listener);
    }

}