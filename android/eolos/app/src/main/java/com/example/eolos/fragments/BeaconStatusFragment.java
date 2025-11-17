/**
 * Fichero: BeaconStatusFragment.java
 * Autor: Hugo Belda
 * Fecha: 29/10/2025
 * Descripción: Fragmento que muestra en tiempo real el estado de conexión con el beacon BLE
 *             y la última medida recibida (valor del minor). Se actualiza mediante
 *             LocalBroadcast desde BeaconScanService.
 */
package com.example.eolos.fragments;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.eolos.R;
import com.example.eolos.servicio.BeaconScanService;

public class BeaconStatusFragment extends Fragment {

    private TextView tvEstado;
    private TextView tvMedida;      // Muestra la medida actual (valor del minor)
    private View cardStatus;

    // =============================================================================
    // CICLO DE VIDA: INFLADO DEL LAYOUT
    // =============================================================================
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_beacon_status, container, false);

        // Vinculación de vistas
        tvEstado    = view.findViewById(R.id.tv_status);
        tvMedida    = view.findViewById(R.id.tv_medida);
        cardStatus  = view.findViewById(R.id.card_status);

        // Estado inicial según servicio
        if (BeaconScanService.isBeaconDetectedRecently()) {
            actualizarEstado("Conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#C8E6C9")); // Verde suave
        } else {
            actualizarEstado("No conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#FFCDD2")); // Rojo suave
        }

        return view;
    }

    // =============================================================================
    // RECEPTOR DE BROADCASTS DEL SERVICIO
    // =============================================================================
    private final BroadcastReceiver beaconReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String json = intent.getStringExtra("json_medida");
            Log.d("BeaconStatusFrag", "Beacon recibido → " + json);

            // Actualizar estado visual
            actualizarEstado("Conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#C8E6C9"));

            // Parsear JSON simple: {"medida": 123}
            try {
                int medida = new org.json.JSONObject(json).getInt("medida");
                tvMedida.setText("Medida: " + medida);
            } catch (Exception e) {
                tvMedida.setText("Medida: —");
                Log.e("BeaconStatusFrag", "Error parseando JSON de medida", e);
            }
        }
    };

    // =============================================================================
    // REGISTRO Y DESREGISTRO DEL RECEPTOR
    // =============================================================================
    @Override
    public void onResume() {
        super.onResume();
        LocalBroadcastManager.getInstance(requireContext())
                .registerReceiver(beaconReceiver,
                        new IntentFilter("com.example.eolos.BEACON_DETECTED"));
    }

    @Override
    public void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(requireContext())
                    .unregisterReceiver(beaconReceiver);
        } catch (Exception ignored) {
            // En caso raro de que ya esté desregistrado
        }
    }

    // =============================================================================
    // ACTUALIZAR ESTADO DE CONEXIÓN
    // =============================================================================
    /**
     * Actualiza el texto y el color de fondo del card según el estado de conexión.
     *
     * @param texto Texto a mostrar ("Conectado" o "No conectado")
     */
    public void actualizarEstado(String texto) {
        if (tvEstado != null) {
            tvEstado.setText(texto);
        }
        if (cardStatus != null) {
            int color = "Conectado".equals(texto)
                    ? Color.parseColor("#C8E6C9")
                    : Color.parseColor("#FFCDD2");
            cardStatus.setBackgroundColor(color);
        }
    }

    // =============================================================================
    // LIMPIAR VALORES (por si en el futuro se añaden más campos)
    // =============================================================================
    /**
     * Limpia los valores mostrados en pantalla (útil para futuras ampliaciones).
     * Actualmente solo se usa tvMedida, pero se mantiene por compatibilidad.
     */
    private void limpiarValores() {
        if (tvMedida != null) {
            tvMedida.setText("Medida: —");
        }
    }
}