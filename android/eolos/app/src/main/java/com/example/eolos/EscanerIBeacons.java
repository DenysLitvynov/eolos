/**
 * Fichero: EscanerIBeacons.java
 * Descripción: Clase que permite escanear iBeacons mediante Bluetooth LE.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 25/09/2025
 */

package com.example.eolos;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Handler;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.util.ArrayList;
import java.util.List;

// --------------------------------------------------------------------
// --------------------------------------------------------------------

public class EscanerIBeacons {
    private static final String ETIQUETA_LOG = ">>>>";
    private static final int CODIGO_PETICION_PERMISOS = 11223344;
    private BluetoothLeScanner elEscanner;
    private ScanCallback callbackDelEscaneo = null;
    public Context context;
    private Handler handler = new Handler();
    private OnBeaconDetectedListener listener;

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    public interface OnBeaconDetectedListener {
        void onBeaconDetected(String jsonMedida);
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    public EscanerIBeacons(Context context, OnBeaconDetectedListener listener) {
        this.context = context;
        this.listener = listener;
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Muestra en Log información completa del dispositivo BLE detectado,
     * incluyendo dirección, RSSI, bytes de la trama y descomposición iBeacon.
     *
     * @param resultado ScanResult del escaneo BLE
     */
    private void mostrarInformacionDispositivoBTLE( ScanResult resultado ) {

        BluetoothDevice bluetoothDevice = resultado.getDevice();
        byte[] bytes = resultado.getScanRecord().getBytes();
        int rssi = resultado.getRssi();

        Log.d(ETIQUETA_LOG, " ****************************************************");
        Log.d(ETIQUETA_LOG, " ****** DISPOSITIVO DETECTADO BTLE ****************** ");
        Log.d(ETIQUETA_LOG, " ****************************************************");
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) { // Android 12+
            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                Log.d(ETIQUETA_LOG, " nombre = " + bluetoothDevice.getName());
            } else {
                Log.d(ETIQUETA_LOG, " nombre = (sin permiso BLUETOOTH_CONNECT)");
            }
        } else { // Android 9 y anteriores
            Log.d(ETIQUETA_LOG, " nombre = " + bluetoothDevice.getName());
        }


        Log.d(ETIQUETA_LOG, " toString = " + bluetoothDevice.toString());

        /*
        ParcelUuid[] puuids = bluetoothDevice.getUuids();
        if ( puuids.length >= 1 ) {
            //Log.d(ETIQUETA_LOG, " uuid = " + puuids[0].getUuid());
           // Log.d(ETIQUETA_LOG, " uuid = " + puuids[0].toString());
        }*/

        Log.d(ETIQUETA_LOG, " dirección = " + bluetoothDevice.getAddress());
        Log.d(ETIQUETA_LOG, " rssi = " + rssi );

        Log.d(ETIQUETA_LOG, " bytes = " + new String(bytes));
        Log.d(ETIQUETA_LOG, " bytes (" + bytes.length + ") = " + Utilidades.bytesToHexString(bytes));

        TramaIBeacon tib = new TramaIBeacon(bytes);

        Log.d(ETIQUETA_LOG, " ----------------------------------------------------");
        Log.d(ETIQUETA_LOG, " prefijo  = " + Utilidades.bytesToHexString(tib.getPrefijo()));
        Log.d(ETIQUETA_LOG, "          advFlags = " + Utilidades.bytesToHexString(tib.getAdvFlags()));
        Log.d(ETIQUETA_LOG, "          advHeader = " + Utilidades.bytesToHexString(tib.getAdvHeader()));
        Log.d(ETIQUETA_LOG, "          companyID = " + Utilidades.bytesToHexString(tib.getCompanyID()));
        Log.d(ETIQUETA_LOG, "          iBeacon type = " + Integer.toHexString(tib.getiBeaconType()));
        Log.d(ETIQUETA_LOG, "          iBeacon length 0x = " + Integer.toHexString(tib.getiBeaconLength()) + " ( "
                + tib.getiBeaconLength() + " ) ");
        Log.d(ETIQUETA_LOG, " uuid  = " + Utilidades.bytesToHexString(tib.getUUID()));
        Log.d(ETIQUETA_LOG, " uuid  = " + Utilidades.bytesToString(tib.getUUID()));
        Log.d(ETIQUETA_LOG, " major  = " + Utilidades.bytesToHexString(tib.getMajor()) + "( "
                + Utilidades.bytesToInt(tib.getMajor()) + " ) ");
        Log.d(ETIQUETA_LOG, " minor  = " + Utilidades.bytesToHexString(tib.getMinor()) + "( "
                + Utilidades.bytesToInt(tib.getMinor()) + " ) ");
        Log.d(ETIQUETA_LOG, " txPower  = " + Integer.toHexString(tib.getTxPower()) + " ( " + tib.getTxPower() + " )");
        Log.d(ETIQUETA_LOG, " ****************************************************");

    } // ()

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Inicia la búsqueda de un dispositivo BLE específico por su nombre.
     *
     * @param dispositivoBuscado Nombre exacto del dispositivo BLE
     */
    private void buscarEsteDispositivoBTLE(final String dispositivoBuscado ) {
        Log.d(ETIQUETA_LOG, " buscarEsteDispositivoBTLE(): empieza ");

        Log.d(ETIQUETA_LOG, "  buscarEsteDispositivoBTLE(): instalamos scan callback ");

        this.callbackDelEscaneo = new ScanCallback() {
            @Override
            public void onScanResult( int callbackType, ScanResult resultado ) {
                super.onScanResult(callbackType, resultado);
                Log.d(ETIQUETA_LOG, "  buscarEsteDispositivoBTLE(): onScanResult() ");

                mostrarInformacionDispositivoBTLE( resultado );

                byte[] bytes = resultado.getScanRecord().getBytes();
                TramaIBeacon tib = new TramaIBeacon(bytes);
                String json = convertirTramaAJson(tib);
                listener.onBeaconDetected(json);
            }

            @Override
            public void onBatchScanResults(List<ScanResult> results) {
                super.onBatchScanResults(results);
                Log.d(ETIQUETA_LOG, "  buscarEsteDispositivoBTLE(): onBatchScanResults() ");

            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
                Log.d(ETIQUETA_LOG, "  buscarEsteDispositivoBTLE(): onScanFailed() ");

            }
        };

        ScanFilter sf = new ScanFilter.Builder().setDeviceName( dispositivoBuscado ).build();

        Log.d(ETIQUETA_LOG, "  buscarEsteDispositivoBTLE(): empezamos a escanear buscando: " + dispositivoBuscado );

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED) {
                List<ScanFilter> filtros = new ArrayList<>();
                filtros.add(sf);

                ScanSettings ajustes = new ScanSettings.Builder()
                        .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                        .build();

                this.elEscanner.startScan(filtros, ajustes, this.callbackDelEscaneo);
            } else {
                Log.e(ETIQUETA_LOG, "No tengo permiso BLUETOOTH_SCAN para iniciar el escaneo");
            }
        } else { // Android 9 y anteriores
            List<ScanFilter> filtros = new ArrayList<>();
            filtros.add(sf);

            ScanSettings ajustes = new ScanSettings.Builder()
                    .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                    .build();

            this.elEscanner.startScan(filtros, ajustes, this.callbackDelEscaneo);
        }

    } // ()
    // ()

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Detiene la búsqueda de dispositivos BLE si hay un callback activo.
     */
    private void detenerBusquedaDispositivosBTLE() {

        if ( this.callbackDelEscaneo == null ) {
            return;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED) {
                this.elEscanner.stopScan(this.callbackDelEscaneo);
            } else {
                Log.e(ETIQUETA_LOG, "No tengo permiso BLUETOOTH_SCAN para detener el escaneo");
            }
        } else { // Android 9 y anteriores
            this.elEscanner.stopScan(this.callbackDelEscaneo);
        }


        this.callbackDelEscaneo = null;

    } // ()

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Inicializa el adaptador Bluetooth del dispositivo.
     * Verifica que Bluetooth esté disponible y habilitado.
     * Solicita los permisos necesarios dependiendo de la versión de Android.
     */
    public void inicializarBlueTooth() {
        Log.i(ETIQUETA_LOG, "Inicializando Bluetooth...");

        BluetoothAdapter bta = BluetoothAdapter.getDefaultAdapter();
        if (bta == null) {
            Log.e(ETIQUETA_LOG, "Error: No hay adaptador Bluetooth disponible en el dispositivo");
            return;
        }

        // Verificar si Bluetooth ya está habilitado
        if (bta.isEnabled()) {
            Log.d(ETIQUETA_LOG, "Bluetooth ya está habilitado");
        } else {
            Log.d(ETIQUETA_LOG, "Bluetooth no está habilitado, se intentará habilitar después de obtener permisos");
            // No intentamos habilitar aquí, lo haremos tras confirmar permisos
        }

        // Obtener el escáner solo si Bluetooth está habilitado
        if (bta.isEnabled()) {
            this.elEscanner = bta.getBluetoothLeScanner();
            if (this.elEscanner == null) {
                Log.e(ETIQUETA_LOG, "Error: No se pudo obtener el escáner Bluetooth LE");
            } else {
                Log.d(ETIQUETA_LOG, "Escáner Bluetooth LE obtenido correctamente");
            }
        }

        // Solicitar permisos si es necesario
        Log.d(ETIQUETA_LOG, "Verificando permisos...");
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED
                    || ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                Log.d(ETIQUETA_LOG, "Solicitando permisos BLUETOOTH_SCAN y BLUETOOTH_CONNECT");
                ActivityCompat.requestPermissions(
                        (android.app.Activity) context,
                        new String[]{Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT},
                        CODIGO_PETICION_PERMISOS
                );
            } else {
                Log.d(ETIQUETA_LOG, "Permisos BLUETOOTH_SCAN y BLUETOOTH_CONNECT ya concedidos");
                // Si los permisos ya están concedidos y Bluetooth no está habilitado, intentar habilitarlo
                if (!bta.isEnabled() && ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                    bta.enable();
                    Log.d(ETIQUETA_LOG, "Bluetooth habilitado");
                }
            }
        } else {
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH) != PackageManager.PERMISSION_GRANTED
                    || ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_ADMIN) != PackageManager.PERMISSION_GRANTED
                    || ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                Log.d(ETIQUETA_LOG, "Solicitando permisos BLUETOOTH, BLUETOOTH_ADMIN y ACCESS_FINE_LOCATION");
                ActivityCompat.requestPermissions(
                        (android.app.Activity) context,
                        new String[]{Manifest.permission.BLUETOOTH, Manifest.permission.BLUETOOTH_ADMIN, Manifest.permission.ACCESS_FINE_LOCATION},
                        CODIGO_PETICION_PERMISOS
                );
            } else {
                Log.d(ETIQUETA_LOG, "Permisos para versiones anteriores ya concedidos");
                if (!bta.isEnabled()) {
                    bta.enable();
                    Log.d(ETIQUETA_LOG, "Bluetooth habilitado");
                }
            }
        }
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Inicia un escaneo de iBeacons de manera automática buscando un dispositivo
     * por su nombre. El escaneo se repite cada 30 segundos.
     *
     * @param nombreDispositivo Nombre exacto del dispositivo BLE a buscar
     */
    public void iniciarEscaneoAutomatico(String nombreDispositivo) {
        inicializarBlueTooth();
        buscarEsteDispositivoBTLE(nombreDispositivo);

        handler.postDelayed(() -> {
            detenerBusquedaDispositivosBTLE();
            buscarEsteDispositivoBTLE(nombreDispositivo);
        }, 30000);
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------

    /**
     * Convierte una trama iBeacon en un JSON simple con la medida
     * contenida en el campo `minor`.
     *
     * @param tib TramaIBeacon detectada durante el escaneo
     * @return String JSON con la medida, por ejemplo: {"medida": 123}
     */
    private String convertirTramaAJson(TramaIBeacon tib) {
        int medida = Utilidades.bytesToInt(tib.getMinor());
        return "{\"medida\": " + medida + "}";
    }
}  // class

// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------