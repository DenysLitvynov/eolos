/**
 * Fichero: EscanerIBeacons.java
 * SOLO escanea el beacon del QR. Ignora TODOS los demás.
 * Implementa patrón singleton y control de duplicados.
 * @author Denys Litvynov Lymanets
 * @editor Hugo Belda Revert
 * @fecha 14/11/2025
 * @version 2.0
 * @since 25/09/2025
 */

package com.example.eolos;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Handler;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.util.HashMap;
import java.util.Map;

public class EscanerIBeacons {
    private static final String ETIQUETA_LOG = ">>>>";
    private static final long DUPLICATE_THRESHOLD_MS = 5000; // ms para filtrar duplicados
    private static EscanerIBeacons instance;

    private BluetoothLeScanner elEscanner;
    private ScanCallback callbackDelEscaneo;
    public Context context;
    private Handler handler = new Handler();
    private OnBeaconDetectedListener listener;
    private Map<String, Long> detectedBeacons = new HashMap<>(); // Direcciones de beacons detectados con timestamp

    // --------------------------------------------------------------------
    // Interfaz callback para notificar detección de beacon
    // --------------------------------------------------------------------
    public interface OnBeaconDetectedListener {
        void onBeaconDetected(String jsonMedida);
    }

    // --------------------------------------------------------------------
    // Constructor privado, asigna contexto y listener
    // --------------------------------------------------------------------
    public EscanerIBeacons(Context context, OnBeaconDetectedListener listener) {
        this.context = context.getApplicationContext();
        this.listener = listener;
    }

    // --------------------------------------------------------------------
    // Patrón singleton: devuelve instancia única
    // --------------------------------------------------------------------
    public static synchronized EscanerIBeacons getInstance(Context context, OnBeaconDetectedListener listener) {
        if (instance == null) {
            instance = new EscanerIBeacons(context, listener);
        }
        instance.listener = listener; // Actualiza listener si se llama de nuevo
        return instance;
    }

    // --------------------------------------------------------------------
    // Muestra información básica del dispositivo BLE detectado
    // Filtra detecciones repetidas en menos de 5s
    // --------------------------------------------------------------------
    private void mostrarInformacionDispositivoBTLE(ScanResult resultado) {
        BluetoothDevice device = resultado.getDevice();
        String address = device.getAddress();
        long now = System.currentTimeMillis();

        // Filtrado de detecciones repetidas
        if (detectedBeacons.containsKey(address) && now - detectedBeacons.get(address) < DUPLICATE_THRESHOLD_MS) {
            Log.d(ETIQUETA_LOG, "Beacon duplicado ignorado: " + address);
            return;
        }

        detectedBeacons.put(address, now);

        byte[] bytes = resultado.getScanRecord() != null ? resultado.getScanRecord().getBytes() : new byte[0];
        int rssi = resultado.getRssi();

        Log.d(ETIQUETA_LOG, "DISPOSITIVO: " + device.getAddress() + " RSSI: " + rssi);
        Log.d(ETIQUETA_LOG, "Bytes del paquete: " + bytes.length);
    }

    // --------------------------------------------------------------------
    // Busca un dispositivo BLE por nombre específico (solo QR)
    // --------------------------------------------------------------------
    private void buscarEsteDispositivoBTLE(String dispositivoBuscado) {
        Log.d(ETIQUETA_LOG, ">>> BUSCANDO SOLO: " + dispositivoBuscado + " <<<");

        // Si ya había un callback activo, lo detenemos
        if (callbackDelEscaneo != null) {
            detenerBusquedaDispositivosBTLE();
        }

        // ----------------------------------------------------------------
        // Configuración del callback del escaneo
        // ----------------------------------------------------------------
        callbackDelEscaneo = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult resultado) {
                super.onScanResult(callbackType, resultado);
                BluetoothDevice bd = resultado.getDevice();
                String name = null;

                // Obtener nombre dependiendo de la versión Android y permisos
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                        name = bd.getName();
                    }
                } else {
                    name = bd.getName();
                }

                // ----------------------------------------------------------------
                // FILTRO ESTRICTO: solo beacon del nombre correcto
                // ----------------------------------------------------------------
                if (name != null && name.equalsIgnoreCase(dispositivoBuscado)) {
                    Log.d(ETIQUETA_LOG, "¡BEACON CORRECTO! -> " + name);

                    // Mostrar información del dispositivo
                    mostrarInformacionDispositivoBTLE(resultado);

                    // Convertir trama iBeacon a JSON y notificar listener
                    byte[] bytes = resultado.getScanRecord().getBytes();
                    TramaIBeacon tib = new TramaIBeacon(bytes);
                    String json = convertirTramaAJson(tib);
                    if (listener != null) {
                        listener.onBeaconDetected(json);
                    }
                }
                // Los demás beacons se ignoran silenciosamente
            }

            @Override
            public void onScanFailed(int errorCode) {
                Log.e(ETIQUETA_LOG, "Escaneo fallido: " + errorCode);
            }
        };

        if (elEscanner == null) {
            Log.e(ETIQUETA_LOG, "Escáner no disponible");
            return;
        }

        // ----------------------------------------------------------------
        // Configuración del escaneo BLE
        // ----------------------------------------------------------------
        ScanSettings settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_POWER)
                .build();

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED) {
                    elEscanner.startScan(null, settings, callbackDelEscaneo);
                }
            } else {
                elEscanner.startScan(null, settings, callbackDelEscaneo);
            }
        } catch (Exception e) {
            Log.e(ETIQUETA_LOG, "Error startScan: " + e.getMessage());
        }
    }

    // --------------------------------------------------------------------
    // Detiene búsqueda de dispositivos BLE si callback activo
    // --------------------------------------------------------------------
    public void detenerBusquedaDispositivosBTLE() {
        if (elEscanner != null && callbackDelEscaneo != null) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED) {
                        elEscanner.stopScan(callbackDelEscaneo);
                    }
                } else {
                    elEscanner.stopScan(callbackDelEscaneo);
                }
            } catch (Exception e) {
                Log.e(ETIQUETA_LOG, "Error stopScan: " + e.getMessage());
            }
        }
        callbackDelEscaneo = null;
    }

    // --------------------------------------------------------------------
    // Inicializa adaptador Bluetooth y escáner BLE
    // --------------------------------------------------------------------
    public void inicializarBlueTooth() {
        BluetoothAdapter bta = BluetoothAdapter.getDefaultAdapter();
        if (bta == null || !bta.isEnabled()) {
            Log.w(ETIQUETA_LOG, "Bluetooth no disponible");
            return;
        }

        elEscanner = bta.getBluetoothLeScanner();
        Log.d(ETIQUETA_LOG, "Escáner BLE inicializado");
    }

    // --------------------------------------------------------------------
    // Inicia escaneo automático del beacon por nombre, repite cada 30s
    // --------------------------------------------------------------------
    public void iniciarEscaneoAutomatico(String nombreDispositivo) {
        if (nombreDispositivo == null || nombreDispositivo.trim().isEmpty()) {
            Log.w(ETIQUETA_LOG, "Nombre vacío - NO escaneo");
            return;
        }

        handler.removeCallbacksAndMessages(null); // Cancelar escaneos previos
        inicializarBlueTooth();
        buscarEsteDispositivoBTLE(nombreDispositivo);

        // Repetir escaneo cada 30 segundos
        handler.postDelayed(() -> {
            detenerBusquedaDispositivosBTLE();
            buscarEsteDispositivoBTLE(nombreDispositivo);
        }, 30000);
    }

    // --------------------------------------------------------------------
    // Convierte trama iBeacon a JSON {"medida": valor}
    // --------------------------------------------------------------------
    private String convertirTramaAJson(TramaIBeacon tib) {
        int medida = Utilidades.bytesToInt(tib.getMinor());
        return "{\"medida\": " + medida + "}";
    }

    // --------------------------------------------------------------------
    // Limpia callbacks, handler y mapa de beacons; destruye instancia singleton
    // --------------------------------------------------------------------
    public void destroy() {
        detenerBusquedaDispositivosBTLE();
        handler.removeCallbacksAndMessages(null);
        detectedBeacons.clear();
        instance = null;
    }
}
