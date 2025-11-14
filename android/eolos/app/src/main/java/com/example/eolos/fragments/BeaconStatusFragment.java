/**
 * Fichero: BeaconStatusFragment.java
 * Autor: Hugo Belda
 * Descripción: Fragmento que muestra el estado de conexión con el emisor BLE.
 * Fecha: 29/10/2025
 */
package com.example.eolos.fragments;

import static androidx.core.content.ContextCompat.registerReceiver;

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

import android.os.Handler;

public class BeaconStatusFragment extends Fragment {

    private TextView tvEstado, tvUuid, tvMajor, tvMinor;
    private View cardStatus;

    private TextView tvMedida;  // Nuevo campo

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_beacon_status, container, false);

        tvEstado = view.findViewById(R.id.tv_status);
        tvMedida = view.findViewById(R.id.tv_medida); // vincular TextView para mostrar medida
        cardStatus = view.findViewById(R.id.card_status);

        if (BeaconScanService.isBeaconDetectedRecently()) {
            actualizarEstado("Conectado");
        } else {
            actualizarEstado("No conectado");
        }

        return view;
    }

    private final BroadcastReceiver beaconReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String json = intent.getStringExtra("json_medida");
            Log.d("BeaconStatusFrag", "Beacon recibido: " + json);
            actualizarEstado("Conectado");

            // Parsear JSON simple {"medida": 123}
            try {
                int medida = new org.json.JSONObject(json).getInt("medida");
                tvMedida.setText("Medida: " + medida);
            } catch (Exception e) {
                tvMedida.setText("Medida: —");
                Log.e("BeaconStatusFrag", "Error parseando medida JSON", e);
            }
        }
    };



    @Override
    public void onResume() {
        super.onResume();
        LocalBroadcastManager.getInstance(requireContext())
                .registerReceiver(beaconReceiver, new IntentFilter("com.example.eolos.BEACON_DETECTED"));
    }

    @Override
    public void onPause() {
        super.onPause();
        LocalBroadcastManager.getInstance(requireContext())
                .unregisterReceiver(beaconReceiver);
    }



    public void actualizarEstado(String texto) {
        tvEstado.setText(texto);
    }

    private void limpiarValores() {
        tvUuid.setText("UUID: —");
        tvMajor.setText("Major: —");
        tvMinor.setText("Minor: —");
    }


}
