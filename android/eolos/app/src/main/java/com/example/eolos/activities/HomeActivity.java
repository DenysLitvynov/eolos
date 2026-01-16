package com.example.eolos.activities;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AlertDialog;
import androidx.biometric.BiometricManager;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.eolos.R;
import com.example.eolos.config.ApiConfig;
import com.example.eolos.servicio.GpsDistanceTrackerService;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.example.eolos.PeticionarioREST;
import com.google.android.material.button.MaterialButton;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class HomeActivity extends AppCompatActivity {

    private TextView tvNombreUsuario, tvAqiValor, tvAqiEstado, tvAqiDescripcion;
    private TextView tvAqiMaximo, tvAqiFechas, tvDistanciaActual, tvEstadoConexion;
    private Spinner spinnerTrayectos;
    private LineChart chartMediciones;
    private LinearLayout containerResumen;
    private ImageView imgAqiIcon;
    private MaterialButton btnCtaMapa, btnCtaRecompensas;

    private List<JSONObject> trayectosDisponibles = new ArrayList<>();
    private String tokenActual;
    private JSONObject trayectoActual;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_page_usuario_registrado);

        // Verificar token
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        tokenActual = prefs.getString("token", null);
        if (tokenActual == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        initViews();
        setupBottomNavigation();
        setupBiometric(prefs);
        
        // Cargar datos
        cargarPerfilUsuario();
        cargarUltimoTrayecto();
    }

    private void initViews() {
        tvNombreUsuario = findViewById(R.id.tv_nombre_usuario);
        tvAqiValor = findViewById(R.id.tv_aqi_valor);
        tvAqiEstado = findViewById(R.id.tv_aqi_estado);
        tvAqiDescripcion = findViewById(R.id.tv_aqi_descripcion);
        tvAqiMaximo = findViewById(R.id.tv_aqi_maximo);
        tvAqiFechas = findViewById(R.id.tv_aqi_fechas);
        tvDistanciaActual = findViewById(R.id.tv_distancia_actual);
        tvEstadoConexion = findViewById(R.id.tv_estado_conexion);
        spinnerTrayectos = findViewById(R.id.spinner_trayectos);
        chartMediciones = findViewById(R.id.chart_mediciones);
        containerResumen = findViewById(R.id.container_resumen);
        imgAqiIcon = findViewById(R.id.img_aqi_icon);
        btnCtaMapa = findViewById(R.id.btn_cta_mapa);
        btnCtaRecompensas = findViewById(R.id.btn_cta_recompensas);

        btnCtaMapa.setOnClickListener(v -> startActivity(new Intent(this, MapaActivity.class)));
        btnCtaRecompensas.setOnClickListener(v -> startActivity(new Intent(this, RecompensaActivity.class)));
    }

    // ===== PETICIÓN: Cargar perfil del usuario =====
    private void cargarPerfilUsuario() {
        new Thread(() -> {
            try {
                PeticionarioREST peticionario = new PeticionarioREST();
                peticionario.hacerPeticionRESTconAuth("GET", ApiConfig.ENDPOINT_PERFIL, null, tokenActual,
                        new PeticionarioREST.RespuestaREST() {
                            @Override
                            public void callback(int codigo, String cuerpo) {
                                if (codigo == 200) {
                                    try {
                                        JSONObject perfil = new JSONObject(cuerpo);
                                        String nombre = perfil.getString("nombre");
                                        runOnUiThread(() -> tvNombreUsuario.setText(nombre));
                                    } catch (Exception e) {
                                        Log.e("HomeActivity", "Error parseando perfil", e);
                                    }
                                } else {
                                    Log.e("HomeActivity", "Error cargando perfil: " + codigo);
                                }
                            }
                        });
            } catch (Exception e) {
                Log.e("HomeActivity", "Error en petición perfil", e);
            }
        }).start();
    }

    // ===== PETICIÓN: Cargar último trayecto =====
    private void cargarUltimoTrayecto() {
        new Thread(() -> {
            try {
                PeticionarioREST peticionario = new PeticionarioREST();
                String url = ApiConfig.ENDPOINT_TRAYECTOS_ULTIMO;

                peticionario.hacerPeticionRESTconAuth("GET", url, null, tokenActual, new PeticionarioREST.RespuestaREST() {
                    @Override
                    public void callback(int codigo, String cuerpo) {
                        if (codigo == 200) {
                            try {
                                trayectoActual = new JSONObject(cuerpo);
                                runOnUiThread(() -> {
                                    actualizarVistaAqi(trayectoActual);
                                    cargarUltimosTrayectos();
                                });
                            } catch (Exception e) {
                                Log.e("HomeActivity", "Error parseando trayecto", e);
                            }
                        } else {
                            Log.e("HomeActivity", "Error cargando trayecto: " + codigo);
                        }
                    }
                });
            } catch (Exception e) {
                Log.e("HomeActivity", "Error en petición trayecto", e);
            }
        }).start();
    }

    // ===== PETICIÓN: Cargar últimos 10 trayectos =====
    private void cargarUltimosTrayectos() {
        new Thread(() -> {
            try {
                PeticionarioREST peticionario = new PeticionarioREST();
                String url = ApiConfig.ENDPOINT_TRAYECTOS_ULTIMOS;

                peticionario.hacerPeticionRESTconAuth("GET", url, null, tokenActual, new PeticionarioREST.RespuestaREST() {
                    @Override
                    public void callback(int codigo, String cuerpo) {
                        if (codigo == 200) {
                            try {
                                JSONArray arr = new JSONArray(cuerpo);
                                trayectosDisponibles.clear();
                                List<String> opciones = new ArrayList<>();

                                for (int i = 0; i < arr.length(); i++) {
                                    JSONObject t = arr.getJSONObject(i);
                                    trayectosDisponibles.add(t);
                                    String fechaInicio = formatearFechaCorta(t.getString("fecha_inicio"));
                                    String fechaFin = formatearFechaCorta(t.getString("fecha_fin"));
                                    opciones.add(fechaInicio + " - " + fechaFin);
                                }

                                runOnUiThread(() -> {
                                    ArrayAdapter<String> adapter = new ArrayAdapter<>(
                                            HomeActivity.this,
                                            android.R.layout.simple_spinner_item,
                                            opciones
                                    );
                                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                                    spinnerTrayectos.setAdapter(adapter);
                                    spinnerTrayectos.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                                        @Override
                                        public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                                            cargarMedicionesTrayecto(trayectosDisponibles.get(position));
                                        }

                                        @Override
                                        public void onNothingSelected(AdapterView<?> parent) {
                                        }
                                    });
                                });
                            } catch (Exception e) {
                                Log.e("HomeActivity", "Error parseando trayectos", e);
                            }
                        }
                    }
                });
            } catch (Exception e) {
                Log.e("HomeActivity", "Error en petición trayectos", e);
            }
        }).start();
    }

    // ===== PETICIÓN: Cargar mediciones de un trayecto =====
    private void cargarMedicionesTrayecto(JSONObject trayecto) {
        new Thread(() -> {
            try {
                String trayectoId = trayecto.getString("trayecto_id");
                PeticionarioREST peticionario = new PeticionarioREST();
                String url = String.format(ApiConfig.ENDPOINT_TRAYECTO_MEDICIONES, trayectoId);

                peticionario.hacerPeticionRESTconAuth("GET", url, null, tokenActual, new PeticionarioREST.RespuestaREST() {
                    @Override
                    public void callback(int codigo, String cuerpo) {
                        if (codigo == 200) {
                            try {
                                JSONArray arr = new JSONArray(cuerpo);
                                List<Entry> entries = new ArrayList<>();
                                for (int i = 0; i < arr.length(); i++) {
                                    JSONObject med = arr.getJSONObject(i);
                                    float aqi = (float) med.getDouble("aqi");
                                    entries.add(new Entry(i, aqi));
                                }

                                runOnUiThread(() -> {
                                    renderizarGrafico(entries);
                                    actualizarResumen(trayecto, entries.size());
                                });
                            } catch (Exception e) {
                                Log.e("HomeActivity", "Error parseando mediciones", e);
                            }
                        }
                    }
                });
            } catch (Exception e) {
                Log.e("HomeActivity", "Error en petición mediciones", e);
            }
        }).start();
    }

    // ===== Actualizar vista AQI =====
    private void actualizarVistaAqi(JSONObject trayecto) {
        try {
            int aqiPromedio = trayecto.getInt("aqi_promedio");
            int aqiMaximo = trayecto.getInt("aqi_maximo");
            int medicionesCount = trayecto.getInt("mediciones_count");
            String fechaInicio = trayecto.getString("fecha_inicio");
            String fechaFin = trayecto.getString("fecha_fin");

            tvAqiValor.setText(String.valueOf(aqiPromedio));
            tvAqiValor.setTextColor(getColorAqi(aqiPromedio));
            tvAqiEstado.setText(getEstadoAqi(aqiPromedio));
            tvAqiDescripcion.setText(getDescripcionAqi(aqiPromedio));
            tvAqiMaximo.setText("Valor máximo: " + aqiMaximo);
            tvAqiFechas.setText("Del " + formatearFecha(fechaInicio) + " al " + formatearFecha(fechaFin));
            imgAqiIcon.setImageResource(getIconoAqi(aqiPromedio));
        } catch (Exception e) {
            Log.e("HomeActivity", "Error actualizando AQI", e);
        }
    }

    // ===== Renderizar gráfico =====
    private void renderizarGrafico(List<Entry> entries) {
        LineDataSet dataSet = new LineDataSet(entries, "AQI");
        dataSet.setColor(Color.BLUE);
        dataSet.setValueTextColor(Color.BLACK);
        dataSet.setLineWidth(2f);
        dataSet.setCircleRadius(4f);

        LineData lineData = new LineData(dataSet);
        chartMediciones.setData(lineData);
        chartMediciones.invalidate();
    }

    // ===== Actualizar resumen =====
    private void actualizarResumen(JSONObject trayecto, int medicionesCount) {
        try {
            containerResumen.removeAllViews();
            float aqiPromedio = (float) trayecto.getDouble("aqi_promedio");
            float distanciaTotal = (float) trayecto.getDouble("distancia_total");

            addResumenItem("Mediciones", String.valueOf(medicionesCount));
            addResumenItem("AQI Promedio", String.format("%.1f", aqiPromedio));
            addResumenItem("Distancia", String.format("%.2f m", distanciaTotal));
        } catch (Exception e) {
            Log.e("HomeActivity", "Error actualizando resumen", e);
        }
    }

    // ===== Agregar item al resumen =====
    private void addResumenItem(String label, String valor) {
        LinearLayout item = new LinearLayout(this);
        item.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        item.setOrientation(LinearLayout.VERTICAL);
        item.setPadding(8, 8, 8, 8);

        TextView tvLabel = new TextView(this);
        tvLabel.setText(label);
        tvLabel.setTextSize(12);
        tvLabel.setTextColor(Color.GRAY);

        TextView tvValor = new TextView(this);
        tvValor.setText(valor);
        tvValor.setTextSize(16);
        tvValor.setTypeface(null, android.graphics.Typeface.BOLD);

        item.addView(tvLabel);
        item.addView(tvValor);
        containerResumen.addView(item);
    }

    // ===== Helpers =====
    private int getColorAqi(int aqi) {
        if (aqi <= 49) return Color.parseColor("#4CAF50");
        if (aqi <= 99) return Color.parseColor("#ffcc00");
        return Color.parseColor("#e53935");
    }

    private String getEstadoAqi(int aqi) {
        if (aqi <= 49) return "Buena";
        if (aqi <= 99) return "Mala";
        return "Poco saludable";
    }

    private String getDescripcionAqi(int aqi) {
        if (aqi <= 49) return "La calidad del aire es buena.";
        if (aqi <= 99) return "Aire poco saludable para grupos sensibles.";
        return "Aire dañino para la salud.";
    }

    private int getIconoAqi(int aqi) {
        if (aqi <= 49) return R.drawable.ic_feliz;
        if (aqi <= 99) return R.drawable.ic_neutral;
        return R.drawable.ic_triste;
    }

    private String formatearFecha(String fechaISO) {
        try {
            SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
            Date fecha = isoFormat.parse(fechaISO);
            SimpleDateFormat displayFormat = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault());
            return displayFormat.format(fecha);
        } catch (ParseException e) {
            return fechaISO;
        }
    }

    private String formatearFechaCorta(String fechaISO) {
        try {
            SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
            Date fecha = isoFormat.parse(fechaISO);
            SimpleDateFormat displayFormat = new SimpleDateFormat("dd/MM HH:mm", Locale.getDefault());
            return displayFormat.format(fecha);
        } catch (ParseException e) {
            return fechaISO;
        }
    }

    private void setupBottomNavigation() {
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        if (iconInicio == null || iconMapa == null) return;

        iconInicio.setOnClickListener(v -> startActivity(new Intent(this, HomeActivity.class)));
        iconMapa.setOnClickListener(v -> startActivity(new Intent(this, MapaActivity.class)));
        iconQR.setOnClickListener(v -> startActivity(new Intent(this, ConnectionActivity.class)));
        iconAlertas.setOnClickListener(v -> startActivity(new Intent(this, IncidenciaActivity.class)));
        iconPerfil.setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }

    private void setupBiometric(SharedPreferences prefs) {
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
                        })
                        .setNegativeButton("Ahora no", (dialog, which) -> {
                            prefs.edit().putBoolean("biometric_asked", true).apply();
                        })
                        .show();
            } else {
                prefs.edit().putBoolean("biometric_asked", true).apply();
            }
        }
    }

    // ===== BroadcastReceiver para GPS =====
    private final BroadcastReceiver distanceReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA.equals(action)) {
                float metros = intent.getFloatExtra(GpsDistanceTrackerService.EXTRA_DISTANCIA, 0f);
                tvDistanciaActual.setText(metros >= 1000
                        ? String.format("%.2f km", metros / 1000f)
                        : String.format("%.1f m", metros));
                tvEstadoConexion.setText("Conectado • GPS activo");
                tvEstadoConexion.setTextColor(Color.parseColor("#2e7d32"));
            } else if (GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO.equals(action)) {
                tvDistanciaActual.setText("0.0 m");
                tvEstadoConexion.setText("Desconectado");
                tvEstadoConexion.setTextColor(Color.parseColor("#999999"));
            }
        }
    };

    @Override
    protected void onResume() {
        super.onResume();
        IntentFilter filter = new IntentFilter();
        filter.addAction(GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA);
        filter.addAction(GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO);
        LocalBroadcastManager.getInstance(this).registerReceiver(distanceReceiver, filter);
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(distanceReceiver);
        } catch (Exception ignored) {
        }
    }
}