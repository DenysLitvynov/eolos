/**
 * Fichero: BeaconStatusFragment.java
 * Descripción: Fragmento que muestra el estado de conexión con el emisor BLE.
 *              Evalúa la última recepción registrada en EscanerSingleton y
 *              actualiza la UI cada segundo.
 * Autor: Hugo Belda
 * Fecha: 29/10/2025
 */

package com.example.eolos.fragments;

import android.os.Bundle;
import android.os.Handler;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.eolos.utils.EscanerSingleton;
import com.example.eolos.R;

public class BeaconStatusFragment extends Fragment {

    private TextView tvStatus;
    private Handler handler = new Handler();
    /**
     * Tarea periódica: verifica la última recepción y actualiza la vista de estado.
     */
    private static final long TIEMPO_MAX_SIN_BEACON = 8000; // si pasan más de 8s sin recepción -> perdida

    private boolean conectado = false;
    private long ultimaRecepcionConfirmada = 0;

    private final Runnable verificarConexion = new Runnable() {
        @Override
        public void run() {
            long ultimaRecepcion = EscanerSingleton.getInstance().getUltimaRecepcion();
            long ahora = System.currentTimeMillis();

            if (ahora - ultimaRecepcion <= 2000) { // beacons llegan con normalidad
                ultimaRecepcionConfirmada = ahora;
                if (!conectado) {
                    conectado = true;
                    tvStatus.setText("Conexión OK");
                }
            } else if (ahora - ultimaRecepcionConfirmada > TIEMPO_MAX_SIN_BEACON) {
                if (conectado) {
                    conectado = false;
                    tvStatus.setText("Conexión perdida");
                }
            }

            handler.postDelayed(this, 1000);
        }
    };

    /**
     * Crea la vista del fragmento, inicializa componentes y arranca el control periódico.
     */
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_beacon_status, container, false);
        tvStatus = view.findViewById(R.id.tv_status);
        handler.post(verificarConexion);
        return view;
    }

    /**
     * Detiene el ciclo de comprobación al destruir la vista, evitando fugas de memoria.
     */
    @Override
    public void onDestroyView() {
        super.onDestroyView();
        handler.removeCallbacks(verificarConexion);
    }
}
