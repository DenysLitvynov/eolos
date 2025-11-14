package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.google.android.material.button.MaterialButton;

public class ConnectionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_conectar_desconectar);

        setupBottomNavigation();
        setupConnectButton();
        setupDisconnectButton();
    }

    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        TextView iconInicio = (TextView) bottomNav.getChildAt(0);
        TextView iconMapa = (TextView) bottomNav.getChildAt(1);
        TextView iconQR = (TextView) bottomNav.getChildAt(2);
        TextView iconAlertas = (TextView) bottomNav.getChildAt(3);
        TextView iconPerfil = (TextView) bottomNav.getChildAt(4);

        iconInicio.setOnClickListener(v -> startActivity(new Intent(this, MainActivity.class)));
        iconMapa.setOnClickListener(v -> Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());
        iconQR.setOnClickListener(v -> Toast.makeText(this, "QR deshabilitado", Toast.LENGTH_SHORT).show());
        iconAlertas.setOnClickListener(v -> Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());
        iconPerfil.setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }

    private void setupConnectButton() {
        MaterialButton conectar = findViewById(R.id.btn_connect);
        conectar.setOnClickListener(v -> startActivity(new Intent(this, QRScannerActivity.class)));
    }

    private void setupDisconnectButton() {
        MaterialButton desconectar = findViewById(R.id.btn_disconnect);
        desconectar.setOnClickListener(v -> Toast.makeText(this, "Desconectado", Toast.LENGTH_SHORT).show());
    }
}
