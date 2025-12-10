package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.eolos.Adapters.RecompensaAdapter;
import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.R;

import java.util.ArrayList;
import java.util.List;

public class RecompensaActivity extends AppCompatActivity {

    private RecyclerView rvDisponibles;
    private RecyclerView rvProximas;
    private ProgressBar progresoKm;
    private TextView tvKmValor;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_recompensas);

        // Header: flecha atrás
        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v -> finish());
        }

        setupBottomNavigation();

        rvDisponibles = findViewById(R.id.rv_recompensas_disponibles);
        rvProximas = findViewById(R.id.rv_proximas_recompensas);
        progresoKm = findViewById(R.id.progreso_km);
        tvKmValor = findViewById(R.id.tv_km_valor);

        rvDisponibles.setLayoutManager(new LinearLayoutManager(this));
        rvProximas.setLayoutManager(new LinearLayoutManager(this));

        rvDisponibles.setNestedScrollingEnabled(false);
        rvProximas.setNestedScrollingEnabled(false);

        rvDisponibles.setAdapter(new RecompensaAdapter(obtenerRecompensasDisponibles()));
        rvProximas.setAdapter(new RecompensaAdapter(obtenerProximasRecompensas()));

        // TODO: sustituir por datos reales (desde backend / SharedPreferences)
        int kmActuales = 15;
        int kmObjetivo = 30;
        tvKmValor.setText(kmActuales + " de " + kmObjetivo + " Km");
        progresoKm.setMax(kmObjetivo);
        progresoKm.setProgress(kmActuales);
    }

    private void setupBottomNavigation() {
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        if (iconInicio != null) {
            iconInicio.setOnClickListener(v ->
                    startActivity(new Intent(this, HomeActivity.class)));
        }

        if (iconMapa != null) {
            iconMapa.setOnClickListener(v ->
                    startActivity(new Intent(this, MapaActivity.class)));
        }

        if (iconQR != null) {
            iconQR.setOnClickListener(v ->
                    startActivity(new Intent(this, ConnectionActivity.class)));
        }

        if (iconAlertas != null) {
            iconAlertas.setOnClickListener(v ->
                    startActivity(new Intent(this, IncidenciaActivity.class)));
        }

        if (iconPerfil != null) {
            iconPerfil.setOnClickListener(v ->
                    startActivity(new Intent(this, PerfilActivity.class)));
        }
    }

    private List<Recompensa_Item> obtenerRecompensasDisponibles() {
        List<Recompensa_Item> list = new ArrayList<>();

        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% menos en tu Mcmenú"
        ));

        list.add(new Recompensa_Item(
                R.drawable.logo_peluqueria,
                "30% menos en corte + lavado"
        ));

        return list;
    }

    private List<Recompensa_Item> obtenerProximasRecompensas() {
        List<Recompensa_Item> list = new ArrayList<>();

        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú"
        ));
        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú"
        ));
        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú"
        ));

        return list;
    }
}
