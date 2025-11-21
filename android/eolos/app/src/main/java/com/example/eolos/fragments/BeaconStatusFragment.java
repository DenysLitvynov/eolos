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
import com.example.eolos.logica_fake.LogicaTrayectosFake;
import com.example.eolos.servicio.BeaconScanService;

public class BeaconStatusFragment extends Fragment {

    private TextView tvEstado;
    private TextView tvMedida;
    private TextView tvTrayectoInfo;
    private View cardStatus;
    private LogicaTrayectosFake logicaTrayectos;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_beacon_status, container, false);

        // Vinculación de vistas
        tvEstado    = view.findViewById(R.id.tv_status);
        tvMedida    = view.findViewById(R.id.tv_medida);
        // tvTrayectoInfo = view.findViewById(R.id.tv_trayecto_info);
        cardStatus  = view.findViewById(R.id.card_status);

        // Inicializar lógica de trayectos
        logicaTrayectos = LogicaTrayectosFake.getInstance(requireContext());

        // Estado inicial según servicio
        if (BeaconScanService.isBeaconDetectedRecently()) {
            actualizarEstado("Conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#C8E6C9")); // Verde suave
        } else {
            actualizarEstado("No conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#FFCDD2")); // Rojo suave
        }

        // Actualizar información del trayecto
        actualizarInfoTrayecto();

        return view;
    }

    private final BroadcastReceiver beaconReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String json = intent.getStringExtra("json_medida");
            Log.d("BeaconStatusFrag", "Beacon recibido → " + json);

            // Actualizar estado visual
            actualizarEstado("Conectado");
            cardStatus.setBackgroundColor(Color.parseColor("#C8E6C9"));

            // Parsear JSON y mostrar medida
            try {
                org.json.JSONObject jsonObj = new org.json.JSONObject(json);
                double valorMedido = jsonObj.getDouble("valor_medido");
                int tipoMedicion = jsonObj.getInt("tipo_medicion");

                String tipoTexto = "";
                switch (tipoMedicion) {
                    case 11: tipoTexto = "PM2.5"; break;
                    case 12: tipoTexto = "PM10"; break;
                    case 13: tipoTexto = "CO2"; break;
                    default: tipoTexto = "Desconocido";
                }

                tvMedida.setText(String.format("Medida: %.2f (%s)", valorMedido, tipoTexto));

                // Actualizar información del trayecto
                actualizarInfoTrayecto();

            } catch (Exception e) {
                tvMedida.setText("Medida: —");
                Log.e("BeaconStatusFrag", "Error parseando JSON de medida", e);
            }
        }
    };

    @Override
    public void onResume() {
        super.onResume();
        LocalBroadcastManager.getInstance(requireContext())
                .registerReceiver(beaconReceiver,
                        new IntentFilter("com.example.eolos.BEACON_DETECTED"));

        // Actualizar información al volver a la actividad
        actualizarInfoTrayecto();
    }

    @Override
    public void onPause() {
        super.onPause();
        try {
            LocalBroadcastManager.getInstance(requireContext())
                    .unregisterReceiver(beaconReceiver);
        } catch (Exception ignored) {
        }
    }

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

    private void actualizarInfoTrayecto() {
        if (tvTrayectoInfo != null) {
            if (logicaTrayectos.estaActivo()) {
                String info = String.format("Trayecto: %s\nBici: %s\nPlaca: %s",
                        logicaTrayectos.getTrayectoId() != null ?
                                logicaTrayectos.getTrayectoId().substring(0, 8) + "..." : "N/A",
                        logicaTrayectos.getBicicletaId() != null ?
                                logicaTrayectos.getBicicletaId() : "N/A",
                        logicaTrayectos.getPlacaId() != null ?
                                logicaTrayectos.getPlacaId().substring(0, 8) + "..." : "N/A");
                tvTrayectoInfo.setText(info);
            } else {
                tvTrayectoInfo.setText("No hay trayecto activo");
            }
        }
    }

    private void limpiarValores() {
        if (tvMedida != null) {
            tvMedida.setText("Medida: —");
        }
        if (tvTrayectoInfo != null) {
            tvTrayectoInfo.setText("No hay trayecto activo");
        }
    }
}