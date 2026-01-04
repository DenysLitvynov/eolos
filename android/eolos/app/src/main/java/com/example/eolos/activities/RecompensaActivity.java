package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
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
import com.example.eolos.logica_fake.RecompensasFake;

import java.util.ArrayList;
import java.util.List;

public class RecompensaActivity extends AppCompatActivity {

    private RecyclerView rvDisponibles;
    private RecyclerView rvProximas;
    private ProgressBar progresoKm;
    private TextView tvKmValor;
    private RecompensasFake clienteRecompensas = new RecompensasFake();


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

        cargarDatosDeRecompensas();


        obtenerKmAcumulados(new RecompensasFake.Km_acumulado_Callback() {
            @Override
            public void onResult(double km) {
                double kmActuales = km;
                double kmObjetivo = 30;
                tvKmValor.setText(kmActuales + " de " + kmObjetivo + " Km");
                progresoKm.setMax((int) kmObjetivo);
                progresoKm.setProgress((int) kmActuales);
            }

            @Override
            public void onError(String error) {
                tvKmValor.setText(0 + " de " + 0 + " Km");
                progresoKm.setMax(0);
                progresoKm.setProgress(0);
                Log.d("recompensas", "onError: ERROR CON LOS KM_ACUMULADOS");
            }
        });
    }

    private void cargarDatosDeRecompensas() {

        // obtenemos los KM acumulados
        obtenerKmAcumulados(new RecompensasFake.Km_acumulado_Callback() {
            @Override
            public void onResult(double km_acumulados) {

                // Luego pedimos todas las recompensas
                clienteRecompensas.obtenerTodasLasRecompensas(new RecompensasFake.RecompensasCallback() {
                    @Override
                    public void onSuccess(List<Recompensa_Item> todasLasRecompensas) {

                        List<Recompensa_Item> disponibles = new ArrayList<>();
                        List<Recompensa_Item> proximas = new ArrayList<>();

                        // Filtramos según crit_num_km de cada recompensa
                        for (Recompensa_Item r : todasLasRecompensas) {
                            if (km_acumulados >= r.get_Crit_num_km()) {
                                disponibles.add(r);
                            } else {
                                proximas.add(r);
                            }
                        }

                        // Actualiza UI
                        runOnUiThread(() -> {
                            rvDisponibles.setAdapter(new RecompensaAdapter(disponibles));
                            rvProximas.setAdapter(new RecompensaAdapter(proximas));
                        });
                    }

                    @Override
                    public void onError(String error) {
                        runOnUiThread(() -> {
                            rvDisponibles.setAdapter(new RecompensaAdapter(new ArrayList<>()));
                            rvProximas.setAdapter(new RecompensaAdapter(new ArrayList<>()));
                        });
                    }
                });
            }

            @Override
            public void onError(String error) {
                // Error obteniendo KM → no podemos filtrar
                rvDisponibles.setAdapter(new RecompensaAdapter(new ArrayList<>()));
                rvProximas.setAdapter(new RecompensaAdapter(new ArrayList<>()));
            }
        });
    }


    // RecompensaActivity.java

    private void obtenerKmAcumulados(RecompensasFake.Km_acumulado_Callback callback) {
        clienteRecompensas.obtener_km_acumulados(new RecompensasFake.Km_acumulado_Callback() {
            @Override
            public void onResult(double km_acumulados) {
                callback.onResult(km_acumulados);
            }

            @Override
            public void onError(String error) {
                callback.onError(error);
            }
        });
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

/*
    //TODO: Filtrar entre disponibles y proximos basados en km(<,o>)
    private List<Recompensa_Item> obtenerRecompensasDisponibles() {
        List<Recompensa_Item> list = new ArrayList<>();

        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% menos en tu Mcmenú",0
        ));

        list.add(new Recompensa_Item(
                R.drawable.logo_peluqueria,
                "30% menos en corte + lavado",0
        ));

        return list;
    }

    private List<Recompensa_Item> obtenerProximasRecompensas() {
        List<Recompensa_Item> list = new ArrayList<>();

        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú",0
        ));
        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú",0
        ));
        list.add(new Recompensa_Item(
                R.drawable.logo_mcdonalds,
                "10% descuento en tu Mcmenú",0
        ));

        return list;
    }
    /
 */
}
