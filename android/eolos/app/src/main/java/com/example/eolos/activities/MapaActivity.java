package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ImageView;
import android.widget.LinearLayout;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;

public class MapaActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mapa);

        setupBottomNavigation();

        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
        }

        WebView web = findViewById(R.id.web_mapa);

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);

        web.setWebViewClient(new WebViewClient());

        web.loadUrl("http://192.168.1.24:8000/pages/mapa_android.html");
    }

    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        if (bottomNav == null) return;

        bottomNav.findViewById(R.id.icon1)
                .setOnClickListener(v -> startActivity(new Intent(this, HomeActivity.class)));

        bottomNav.findViewById(R.id.icon2)
                .setOnClickListener(v -> startActivity(new Intent(this, MapaActivity.class)));

        bottomNav.findViewById(R.id.icon3)
                .setOnClickListener(v -> startActivity(new Intent(this, ConnectionActivity.class)));

        bottomNav.findViewById(R.id.icon4)
                .setOnClickListener(v -> startActivity(new Intent(this, IncidenciaActivity.class)));

        bottomNav.findViewById(R.id.icon5)
                .setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }
}
