/**
 * Fichero: EscanerIBeacons.java
 * Versión mejorada: devuelve TODOS los datos del beacon (RSSI, MAC, major, minor, tipo, contador...)
 *
 * @author  Denys Litvynov Lymanets
 * @editor  Hugo Belda Revert
 * @fecha   18/11/2025
 * @version 3.0
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
    private static final long DUPLICATE_THRESHOLD_MS = 3000;
    private static final long REPEAT_SCAN_MS = 30_000;

    private static EscanerIBeacons instance;

    private BluetoothLeScanner scanner;
    private ScanCallback scanCallback;
    public Context context;
    private final Handler handler = new Handler();
    private OnBeaconDetectedListener listener;
    private final Map<String, Long> lastSeen = new HashMap<>();
    private String idBici = "sin_asignar";

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

    public void setIdBici(String id) {
        this.idBici = (id != null) ? id : "sin_asignar";
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
        Log.d(TAG, "Detectado → " + address + " | RSSI: " + rssi + " dBm");
    }

    // =============================================================================
    // ESCANEO EXCLUSIVO POR UUID
    // =============================================================================
    /**
     * Inicia el escaneo BLE filtrando exclusivamente por el uuid del beacon indicado.
     *
     * @param uuidBuscado uuid exacto del beacon a buscar
     */
    private void buscarPorUUID(final String uuidBuscado) {
        Log.d(TAG, ">>> BUSCANDO POR UUID: " + uuidBuscado + " <<<");

        if (scanCallback != null) detenerBusquedaDispositivosBTLE();

        scanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                byte[] record = result.getScanRecord().getBytes();
                if (record == null || record.length < 25) return;

                // === EXTRAER UUID (bytes 9–24) ===
                StringBuilder uuidBuilder = new StringBuilder();
                for (int i = 9; i < 25; i++) {
                    uuidBuilder.append(String.format("%02X", record[i]));
                }
                String uuidDetectado = uuidBuilder.toString();
                uuidDetectado = uuidDetectado.substring(0,8) + "-" +
                        uuidDetectado.substring(8,12) + "-" +
                        uuidDetectado.substring(12,16) + "-" +
                        uuidDetectado.substring(16,20) + "-" +
                        uuidDetectado.substring(20,32);

                if (!uuidDetectado.equalsIgnoreCase(uuidBuscado)) {
                    return; // No es nuestro beacon → ignorar
                }

                Log.d(TAG, "BEACON CORRECTO → " + uuidDetectado);
                mostrarInformacionDispositivoBTLE(result);

                // === PARSEAR TRAMA iBeacon ===
                TramaIBeacon trama = new TramaIBeacon(record);

                int majorRaw = Utilidades.bytesToInt(trama.getMajor());
                int tipoMedicion = (majorRaw >> 8) & 0xFF;   // 11=CO2, 12=Temperatura, 13=Ruido...
                int contador = majorRaw & 0xFF;

                int minorRaw = Utilidades.bytesToInt(trama.getMinor());
                float valorMedido = minorRaw / 1000.0f; // porque en el ESP32 multiplicamos ×1000

                String mac = result.getDevice().getAddress();
                String nombreBeacon = "desconocido";

                try {
                    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S ||
                            ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT)
                                    == PackageManager.PERMISSION_GRANTED) {

                        String tempName = result.getDevice().getName();
                        if (tempName != null && !tempName.isEmpty()) {
                            nombreBeacon = tempName;
                        }
                    }
                } catch (Exception e) {
                    // Si explota por permiso → se queda "desconocido"
                    Log.w(TAG, "No se pudo leer el nombre del beacon (sin permiso BLUETOOTH_CONNECT)");
                }                if (nombreBeacon == null || nombreBeacon.isEmpty()) {
                    nombreBeacon = "desconocido";
                }
                int rssi = result.getRssi();

                // === JSON COMPLETO CON TODO ===
                String jsonCompleto = String.format(
                        "{"
                                + "\"uuid\":\"%s\","
                                + "\"mac\":\"%s\","
                                + "\"nombre\":\"%s\","
                                + "\"rssi\":%d,"
                                + "\"major\":%d,"
                                + "\"tipo_medicion\":%d,"
                                + "\"contador\":%d,"
                                + "\"minor\":%d,"
                                + "\"valor_medido\":%.3f,"
                                + "\"id_bici\":\"%s\""
                                + "}",
                        uuidDetectado,
                        mac,
                        nombreBeacon,           // ← NUEVO: nombre del beacon
                        rssi,
                        majorRaw,
                        tipoMedicion,
                        contador,
                        minorRaw,
                        valorMedido,
                        idBici
                );

                Log.i(TAG, "TRAMA COMPLETA → " + jsonCompleto);

                if (listener != null) {
                    listener.onBeaconDetected(jsonCompleto);
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                Log.e(TAG, "Escaneo fallido → código: " + errorCode);
            }
        };

        if (scanner == null) {
            inicializarBlueTooth();
            if (scanner == null) {
                Log.e(TAG, "No se pudo inicializar Bluetooth LE Scanner");
                return;
            }
        }

        ScanSettings settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)  // Más rápido para pruebas
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
            Log.d(TAG, "Escaneo iniciado correctamente");
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
        if (scanner != null) {
            Log.d(TAG, "Bluetooth LE Scanner inicializado");
        }
    }

    // =============================================================================
    // ESCANEO AUTOMÁTICO CADA 30 SEGUNDOS
    // =============================================================================
    /**
     * Inicia el escaneo automático del beacon indicado. Detiene cualquier escaneo previo,
     * realiza un primer escaneo inmediato y lo repite cada 30 segundos.
     *
     * @param uuid uuid exacto del beacon a escanear
     */
    public void iniciarEscaneoAutomatico(String uuid) {
        if (uuid == null || uuid.trim().isEmpty()) return;

        handler.removeCallbacksAndMessages(null);
        inicializarBlueTooth();
        buscarPorUUID(uuid);

        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                detenerBusquedaDispositivosBTLE();
                buscarPorUUID(uuid);
            }
        }, REPEAT_SCAN_MS);
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