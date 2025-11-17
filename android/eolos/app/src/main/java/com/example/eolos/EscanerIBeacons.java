/**
 * Fichero: EscanerIBeacons.java
 * SOLO escanea el beacon cuyo nombre viene en el QR. Ignora TODOS los demás.
 * Patrón singleton + filtro anti-duplicados (5 s).
 *
 * @author  Denys Litvynov Lymanets
 * @editor  Hugo Belda Revert
 * @fecha   14/11/2025
 * @version 2.0
 * @since   25/09/2025
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
import java.util.HashMap;
import java.util.Map;

public class EscanerIBeacons {

    private static final String TAG = ">>>>";
    private static final long DUPLICATE_THRESHOLD_MS = 5000;   // Ignorar duplicados < 5 s
    private static final long REPEAT_SCAN_MS = 30_000;         // Repetir cada 30 s

    private static EscanerIBeacons instance;

    private BluetoothLeScanner scanner;
    private ScanCallback scanCallback;
    public Context context;
    private final Handler handler = new Handler();
    private OnBeaconDetectedListener listener;
    private final Map<String, Long> lastSeen = new HashMap<>(); // MAC → timestamp

    // =============================================================================
    // CALLBACK
    // =============================================================================
    /**
     * Interfaz callback para notificar detección de beacon
     */
    public interface OnBeaconDetectedListener {
        void onBeaconDetected(String jsonMedida);
    }

    // =============================================================================
    // CONSTRUCTOR PRIVADO (Singleton)
    // =============================================================================
    /**
     * Constructor privado (singleton).
     *
     * @param context  Contexto de la aplicación
     * @param listener Listener que recibirá las medidas cuando se detecte el beacon correcto
     */
    private EscanerIBeacons(Context context, OnBeaconDetectedListener listener) {
        this.context = context.getApplicationContext();
        this.listener = listener;
    }

    // =============================================================================
    // SINGLETON
    // =============================================================================
    /**
     * Obtiene la única instancia de EscanerIBeacons (patrón Singleton).
     * Si ya existe, actualiza el listener.
     *
     * @param context  Contexto de la aplicación
     * @param listener Listener para recibir las detecciones
     * @return Instancia única de EscanerIBeacons
     */
    public static synchronized EscanerIBeacons getInstance(Context context, OnBeaconDetectedListener listener) {
        if (instance == null) {
            instance = new EscanerIBeacons(context, listener);
        }
        instance.listener = listener;
        return instance;
    }

    // =============================================================================
    // FILTRADO DE DUPLICADOS + LOG
    // =============================================================================
    /**
     * Muestra información del dispositivo detectado y filtra duplicados en menos de 5 segundos.
     *
     * @param resultado Resultado del escaneo BLE
     */
    private void mostrarInformacionDispositivoBTLE(ScanResult resultado) {
        BluetoothDevice device = resultado.getDevice();
        String address = device.getAddress();
        long now = System.currentTimeMillis();

        if (lastSeen.containsKey(address) && now - lastSeen.get(address) < DUPLICATE_THRESHOLD_MS) {
            Log.d(TAG, "Duplicado ignorado → " + address);
            return;
        }
        lastSeen.put(address, now);

        int rssi = resultado.getRssi();
        Log.d(TAG, "Detectado → " + address + " | RSSI: " + rssi);
    }

    // =============================================================================
    // ESCANEO EXCLUSIVO POR NOMBRE
    // =============================================================================
    /**
     * Inicia el escaneo BLE filtrando exclusivamente por el nombre del beacon indicado.
     *
     * @param dispositivoBuscado Nombre exacto del beacon a buscar (case-insensitive)
     */
    private void buscarEsteDispositivoBTLE(String dispositivoBuscado) {
        Log.d(TAG, ">>> BUSCANDO EXCLUSIVAMENTE: " + dispositivoBuscado + " <<<");

        if (scanCallback != null) detenerBusquedaDispositivosBTLE();

        scanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                BluetoothDevice device = result.getDevice();
                String name = null;

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT)
                            == PackageManager.PERMISSION_GRANTED) {
                        name = device.getName();
                    }
                } else {
                    name = device.getName();
                }

                if (name != null && name.equalsIgnoreCase(dispositivoBuscado)) {
                    Log.d(TAG, "¡BEACON CORRECTO ENCONTRADO! → " + name);
                    mostrarInformacionDispositivoBTLE(result);

                    byte[] record = result.getScanRecord().getBytes();
                    TramaIBeacon trama = new TramaIBeacon(record);
                    String json = convertirTramaAJson(trama);
                    if (listener != null) listener.onBeaconDetected(json);
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                Log.e(TAG, "Escaneo fallido → código: " + errorCode);
            }
        };

        if (scanner == null) {
            Log.e(TAG, "Scanner no inicializado");
            return;
        }

        ScanSettings settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_POWER)
                .build();

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN)
                        == PackageManager.PERMISSION_GRANTED) {
                    scanner.startScan(null, settings, scanCallback);
                }
            } else {
                scanner.startScan(null, settings, scanCallback);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error al iniciar escaneo → " + e.getMessage());
        }
    }

    // =============================================================================
    // DETENER ESCANEO
    // =============================================================================
    /**
     * Detiene el escaneo BLE actual si está en curso.
     */
    public void detenerBusquedaDispositivosBTLE() {
        if (scanner != null && scanCallback != null) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN)
                            == PackageManager.PERMISSION_GRANTED) {
                        scanner.stopScan(scanCallback);
                    }
                } else {
                    scanner.stopScan(scanCallback);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error al detener escaneo → " + e.getMessage());
            }
        }
        scanCallback = null;
    }

    // =============================================================================
    // INICIALIZAR BLUETOOTH
    // =============================================================================
    /**
     * Inicializa el adaptador Bluetooth y obtiene el BluetoothLeScanner.
     * Si Bluetooth no está disponible o desactivado, registra advertencia.
     */
    public void inicializarBlueTooth() {
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null || !adapter.isEnabled()) {
            Log.w(TAG, "Bluetooth no disponible o desactivado");
            return;
        }
        scanner = adapter.getBluetoothLeScanner();
        Log.d(TAG, "Bluetooth LE inicializado correctamente");
    }

    // =============================================================================
    // ESCANEO AUTOMÁTICO CADA 30 SEGUNDOS
    // =============================================================================
    /**
     * Inicia el escaneo automático del beacon indicado. Detiene cualquier escaneo previo,
     * realiza un primer escaneo inmediato y lo repite cada 30 segundos.
     *
     * @param nombreDispositivo Nombre exacto del beacon a escanear
     */
    public void iniciarEscaneoAutomatico(String nombreDispositivo) {
        if (nombreDispositivo == null || nombreDispositivo.trim().isEmpty()) {
            Log.w(TAG, "Nombre vacío → no se inicia escaneo");
            return;
        }

        handler.removeCallbacksAndMessages(null);
        inicializarBlueTooth();
        buscarEsteDispositivoBTLE(nombreDispositivo);

        handler.postDelayed(() -> {
            detenerBusquedaDispositivosBTLE();
            buscarEsteDispositivoBTLE(nombreDispositivo);
        }, REPEAT_SCAN_MS);
    }

    // =============================================================================
    // CONVERSIÓN A JSON
    // =============================================================================
    /**
     * Convierte la trama iBeacon en un JSON con la medida (minor).
     *
     * @param tib Objeto TramaIBeacon con los datos del paquete recibido
     * @return String JSON con formato {"medida": valor}
     */
    private String convertirTramaAJson(TramaIBeacon tib) {
        int medida = Utilidades.bytesToInt(tib.getMinor());
        return "{\"medida\": " + medida + "}";
    }

    // =============================================================================
    // LIMPIEZA TOTAL Y DESTRUCCIÓN DE INSTANCIA
    // =============================================================================
    /**
     * Detiene el escaneo, limpia todos los recursos y destruye la instancia singleton.
     * Debe llamarse al cerrar la aplicación o al desconectar.
     */
    public void destroy() {
        detenerBusquedaDispositivosBTLE();
        handler.removeCallbacksAndMessages(null);
        lastSeen.clear();
        instance = null;
        Log.d(TAG, "EscanerIBeacons destruido");
    }
}