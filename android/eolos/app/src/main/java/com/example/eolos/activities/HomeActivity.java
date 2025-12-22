package com.example.eolos.activities;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.biometric.BiometricManager;
import androidx.core.app.ActivityCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.eolos.R;
import com.example.eolos.logica_fake.HomeFake;
import com.example.eolos.servicio.GpsDistanceTrackerService;

import java.util.List;

public class HomeActivity extends AppCompatActivity {

    private static final String TAG = "HomeActivity";

    // ===== Views: gases dinámicos =====
    private LinearLayout gasContainer;

    // ===== Views: AQI / impacto / trayecto =====
    private ImageView dotCalidad;
    private TextView tvImpactoTexto, tvUltimoDetalle;
    private TextView tvAqiValor, tvAqiEstado, tvAqiDescripcion;

    // ===== Views: trayecto actual (distancia live) =====
    private View contenedorTrayectoActual;
    private TextView tvDistanciaActual;
    private TextView tvEstadoConexion;

    // ===== Data loader =====
    private HomeFake homeFake;

    //------------------------------------------------------------------------------------------
    // onCreate
    //------------------------------------------------------------------------------------------
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home_page_usuario_registrado);

        setupBottomNavigation();

        // Botones
        Button btnVerMapa = findViewById(R.id.btnVerMapa);
        btnVerMapa.setOnClickListener(v -> startActivity(new Intent(HomeActivity.this, MapaActivity.class)));

        Button btnVerInfo = findViewById(R.id.btn_ver_info);
        btnVerInfo.setOnClickListener(v -> startActivity(new Intent(this, CalidadAireActivity.class)));

        Button btnVerRecompensas = findViewById(R.id.btn_ver_recompensas);
        btnVerRecompensas.setOnClickListener(v -> startActivity(new Intent(this, RecompensaActivity.class)));

        // Bind views (XML ya tiene estos IDs)
        gasContainer = findViewById(R.id.gasContainer);

        dotCalidad = findViewById(R.id.dot_calidad);
        tvImpactoTexto = findViewById(R.id.tv_impacto_texto);
        tvUltimoDetalle = findViewById(R.id.tv_ultimo_detalle);

        tvAqiValor = findViewById(R.id.tv_aqi_valor);
        tvAqiEstado = findViewById(R.id.tv_aqi_estado);
        tvAqiDescripcion = findViewById(R.id.tv_aqi_descripcion);

        contenedorTrayectoActual = findViewById(R.id.contenedor_trayecto_actual);
        tvDistanciaActual = findViewById(R.id.tv_distancia_actual);
        tvEstadoConexion = findViewById(R.id.tv_estado_conexion);

        homeFake = new HomeFake(this);

        // Verificar token (igual que tu lógica)
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        // Biometría (tu lógica)
        boolean biometricAsked = prefs.getBoolean("biometric_asked", false);
        if (!biometricAsked) {
            BiometricManager biometricManager = BiometricManager.from(this);
            int canAuth = biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG);

            if (canAuth == BiometricManager.BIOMETRIC_SUCCESS) {
                new AlertDialog.Builder(this)
                        .setTitle(getString(R.string.biometric_enable_title))
                        .setMessage(getString(R.string.biometric_enable_message))
                        .setPositiveButton("Sí", (dialog, which) -> {
                            prefs.edit()
                                    .putBoolean("biometric_enabled", true)
                                    .putBoolean("biometric_asked", true)
                                    .apply();

                            Toast.makeText(HomeActivity.this, "Inicio con huella activado", Toast.LENGTH_SHORT).show();

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
                        .setNegativeButton("Ahora no", (dialog, which) ->
                                prefs.edit().putBoolean("biometric_asked", true).apply()
                        )
                        .show();
            } else {
                prefs.edit().putBoolean("biometric_asked", true).apply();
            }
        }

        // Mostrar estado inicial del bloque trayecto actual según service
        syncTrayectoActualUIWithServiceState();

        // Cargar datos reales de home
        cargarDatosHome();
    }

    //------------------------------------------------------------------------------------------
    // Cargar Home real desde backend (con GPS opcional)
    //------------------------------------------------------------------------------------------
    private void cargarDatosHome() {
        Double[] loc = getLastKnownLatLonOrNull();
        Double lat = loc[0];
        Double lon = loc[1];

        homeFake.cargarHome(lat, lon, (ok, code, raw, home) -> runOnUiThread(() -> {
            if (!ok) {
                Log.e(TAG, "Home FAIL code=" + code + " body=" + raw);
                Toast.makeText(HomeActivity.this, "No se pudo cargar Home (" + code + ")", Toast.LENGTH_SHORT).show();
                renderEmptyHomeUI();
                return;
            }
            renderHomeUI(home);
        }));
    }

    private Double[] getLastKnownLatLonOrNull() {
        Double[] out = new Double[]{null, null};

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED
                && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            return out; // sin permisos -> no GPS -> backend fallback
        }

        try {
            LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
            if (lm == null) return out;

            Location gps = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            Location net = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);

            Location best = null;
            if (gps != null) best = gps;
            if (net != null && (best == null || net.getTime() > best.getTime())) best = net;

            if (best != null) {
                out[0] = best.getLatitude();
                out[1] = best.getLongitude();
            }
        } catch (Exception e) {
            Log.w(TAG, "getLastKnownLatLonOrNull error: " + e.getMessage());
        }

        return out;
    }

    //------------------------------------------------------------------------------------------
    // Render UI
    //------------------------------------------------------------------------------------------
    private void renderHomeUI(HomeFake home) {
        // gases dinámicos (todos los tipos)
        renderGasesDynamic(home.getGases());

        // impacto
        String impacto = "“Has contribuido con " + home.getRutasLimpias() + " rutas limpias”\n"
                + "o “Evitaste " + format2(home.getCo2Kg()) + " kg de CO₂”\n\n"
                + "“Tienes " + home.getPuntos() + " puntos para canjear en Valenbisi”";
        tvImpactoTexto.setText(impacto);

        // último trayecto
        Double dist = home.getUltimoDistKm();
        Integer tmin = home.getUltimoTiempoMin();
        String cal = home.getUltimoCalidadPromedio();

        String ultimo = "Distancia: " + (dist == null ? "-" : format1(dist) + " km") + "\n"
                + "Tiempo: " + (tmin == null ? "-" : tmin + " min");
        tvUltimoDetalle.setText(ultimo);

        // dot calidad (promedio)
        applyDotCalidad(cal != null ? cal : home.getAqiEstado());

        // AQI card
        tvAqiValor.setText(home.getAqiScore() == null ? "--" : home.getAqiScore());
        tvAqiEstado.setText(mapAqiEstadoToShort(home.getAqiEstado()));
        tvAqiDescripcion.setText(home.getAqiDescripcion() == null ? "" : home.getAqiDescripcion());

        Log.d(TAG, "Home OK placa_id=" + home.getPlacaId());
    }

    private void renderEmptyHomeUI() {
        renderGasesDynamic(null);

        tvImpactoTexto.setText("—");
        tvUltimoDetalle.setText("Distancia: - km\nTiempo: - min");

        tvAqiValor.setText("--");
        tvAqiEstado.setText("—");
        tvAqiDescripcion.setText("—");

        applyDotCalidad(null);
    }

    //------------------------------------------------------------------------------------------
    // Gases dinámicos
    //------------------------------------------------------------------------------------------
    private void renderGasesDynamic(List<HomeFake.GasItem> gases) {
        if (gasContainer == null) return;

        gasContainer.removeAllViews();

        if (gases == null || gases.isEmpty()) {
            TextView tv = new TextView(this);
            tv.setText("Sin datos de gases para este sensor.");
            tv.setTextSize(14);
            gasContainer.addView(tv);
            return;
        }

        for (HomeFake.GasItem g : gases) {
            View row = getLayoutInflater().inflate(R.layout.item_gas_row, gasContainer, false);

            TextView tvGas = row.findViewById(R.id.tvGasRowText);

            String tipo = (g.tipo == null || g.tipo.trim().isEmpty()) ? "gas" : g.tipo;
            String valor = (g.valor == null) ? "-" : format2(g.valor);

            tvGas.setText(tipo + ": " + valor);



            gasContainer.addView(row);
        }
    }

    //------------------------------------------------------------------------------------------
    // Helpers formato / estado
    //------------------------------------------------------------------------------------------
    private String format1(double v) {
        return String.format(java.util.Locale.US, "%.1f", v);
    }

    private String format2(double v) {
        return String.format(java.util.Locale.US, "%.2f", v);
    }

    private String mapAqiEstadoToShort(String estado) {
        if (estado == null) return "—";
        String st = estado.trim().toLowerCase();
        if (st.equals("buena")) return "Bien";
        if (st.equals("mala")) return "Mala";
        if (st.equals("poco saludable")) return "Poco Saludable";
        return estado;
    }

    private void applyDotCalidad(String estado) {
        if (dotCalidad == null) return;
        if (estado == null) {
            dotCalidad.setBackgroundResource(R.drawable.circulo_amarillo);
            return;
        }
        String st = estado.trim().toLowerCase();
        if (st.equals("buena")) {
            dotCalidad.setBackgroundResource(R.drawable.circulo_verde);
        } else if (st.equals("poco saludable")) {
            dotCalidad.setBackgroundResource(R.drawable.circulo_rojo);
        } else {
            dotCalidad.setBackgroundResource(R.drawable.circulo_amarillo);
        }
    }

    //------------------------------------------------------------------------------------------
    // Trayecto actual UI init (si service ya está corriendo)
    //------------------------------------------------------------------------------------------
    private void syncTrayectoActualUIWithServiceState() {
        if (contenedorTrayectoActual == null) return;

        if (GpsDistanceTrackerService.isRunning()) {
            contenedorTrayectoActual.setVisibility(View.VISIBLE);
            tvEstadoConexion.setText("Conectado al sensor • GPS activo");
        } else {
            // 如果你想默认隐藏就用 GONE；想显示就用 VISIBLE 并显示断开文案
            contenedorTrayectoActual.setVisibility(View.VISIBLE);
            tvEstadoConexion.setText("sin Conectado al sensor • GPS inactivo");
        }
    }

    //------------------------------------------------------------------------------------------
    // Bottom navigation
    //------------------------------------------------------------------------------------------
    private void setupBottomNavigation() {
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        iconInicio.setOnClickListener(v -> startActivity(new Intent(this, HomeActivity.class)));
        iconMapa.setOnClickListener(v -> startActivity(new Intent(this, MapaActivity.class)));
        iconQR.setOnClickListener(v -> startActivity(new Intent(this, ConnectionActivity.class)));
        iconAlertas.setOnClickListener(v -> startActivity(new Intent(this, IncidenciaActivity.class)));
        iconPerfil.setOnClickListener(v -> startActivity(new Intent(this, PerfilActivity.class)));
    }

    //------------------------------------------------------------------------------------------
    // Receiver: DISTANCIA + ESTADO (usa EXACTAMENTE tus actions)
    //------------------------------------------------------------------------------------------
    private final BroadcastReceiver distanceReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            if (intent == null) return;

            String action = intent.getAction();
            if (action == null) return;

            if (GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA.equals(action)) {
                float metros = intent.getFloatExtra(GpsDistanceTrackerService.EXTRA_DISTANCIA, 0f);

                if (contenedorTrayectoActual != null) contenedorTrayectoActual.setVisibility(View.VISIBLE);

                if (tvDistanciaActual != null) {
                    tvDistanciaActual.setText(metros >= 1000
                            ? String.format(java.util.Locale.US, "%.2f km", metros / 1000f)
                            : String.format(java.util.Locale.US, "%.1f m", metros));
                }

                if (tvEstadoConexion != null) {
                    tvEstadoConexion.setText("Conectado al sensor • GPS activo");
                }

            } else if (GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO.equals(action)) {
                float metrosFinal = intent.getFloatExtra(GpsDistanceTrackerService.EXTRA_DISTANCIA, 0f);
                Log.d(TAG, "Servicio detenido, distancia final=" + metrosFinal);

                if (contenedorTrayectoActual != null) contenedorTrayectoActual.setVisibility(View.GONE);

                if (tvDistanciaActual != null) tvDistanciaActual.setText("0.0 m");

                if (tvEstadoConexion != null) {
                    tvEstadoConexion.setText("Sensor desconectado • GPS inactivo");
                }
            }
        }
    };

    @Override
    protected void onResume() {
        super.onResume();

        // register receiver
        IntentFilter filter = new IntentFilter();
        filter.addAction(GpsDistanceTrackerService.ACCION_ACTUALIZAR_DISTANCIA);
        filter.addAction(GpsDistanceTrackerService.ACCION_SERVICIO_DETENIDO);
        LocalBroadcastManager.getInstance(this).registerReceiver(distanceReceiver, filter);

        syncTrayectoActualUIWithServiceState();

        cargarDatosHome();
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(this).unregisterReceiver(distanceReceiver);
        } catch (Exception ignored) {}
    }
}
