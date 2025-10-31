/**
 * Fichero: BeaconScanService.java
 * Descripción: Servicio en primer plano que escanea beacons BLE y muestra
 *              una notificación persistente. Al tocar la notificación se
 *              vuelve a la app (sin cerrar el servicio). Incluye acción "Stop".
 * Autor: JINWEI
 * Fecha: 31/10/2025
 */

package com.example.eolos.servicio;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;

import com.example.eolos.TramaIBeacon;
import com.example.eolos.Utilidades;
import com.example.eolos.activities.MainActivity; // ⚠️ Ajusta si tu MainActivity está en otro paquete

import java.util.ArrayList;
import java.util.List;

public class BeaconScanService extends Service {

    // ====== Configuración =======================================================================

    private static final String TARGET_DEVICE_NAME = "pincun F8pro"; // Nombre del beacon objetivo

    private static final String TAG = "BeaconSvc";
    private static final String ETIQUETA_LOG = ">>>>>";

    public static final String ACTION_STATUS = "com.example.sprint1.STATUS";
    public static final String EXTRA_OK   = "ok";
    public static final String EXTRA_STEP = "step";
    public static final String EXTRA_MSG  = "msg";

    private static final String ACTION_STOP = "ACTION_STOP_BEACON_SCAN"; // Acción para detener
    private static final int NOTIF_ID = 1; // ID de notificación

    private BluetoothLeScanner scanner;

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "Service onCreate()");
        ensureChannel(); // Crear canal de notificación si no existe
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.i(TAG, "onStartCommand()");

        // Si se pulsa el botón "Stop" desde la notificación:
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            Log.i(TAG, "Recibido ACTION_STOP, deteniendo servicio.");
            stopScan();
            stopForeground(true);
            stopSelf();
            return START_NOT_STICKY;
        }

        // ✅ Intent para volver a la app sin destruir el servicio
        Intent openApp = new Intent(this, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);

        PendingIntent contentPi = PendingIntent.getActivity(
                this,
                100,
                openApp,
                (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
                        ? PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
                        : PendingIntent.FLAG_UPDATE_CURRENT
        );

        // ✅ Acción "Stop" en la notificación
        Intent stop = new Intent(this, BeaconScanService.class).setAction(ACTION_STOP);
        PendingIntent stopPi = PendingIntent.getService(
                this,
                101,
                stop,
                (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
                        ? PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
                        : PendingIntent.FLAG_UPDATE_CURRENT
        );

        // ✅ Construcción de notificación persistente
        Notification notification = new NotificationCompat.Builder(this, PermisosHelper.CHANNEL_ID)
                .setContentTitle("Escaneo de beacons activo")
                .setContentText("Pulsar para volver a la aplicación")
                .setSmallIcon(android.R.drawable.stat_sys_data_bluetooth)
                .setOngoing(true)          // Notificación fija
                .setAutoCancel(false)      // << Clave: no se borra al tocar
                .setContentIntent(contentPi) // Tocar → volver a MainActivity
                .addAction(0, "Stop", stopPi) // Botón "Stop"
                .build();

        startForeground(NOTIF_ID, notification); // Servicio en primer plano

        startScan(); // Iniciar escaneo BLE

        return START_STICKY; // Mantener vivo si el sistema lo mata
    }

    /**
     * Inicia el escaneo BLE con validaciones y permisos.
     */
    private void startScan() {
        sendStatus(true, "CHECK_BT_ADAPTER", "BluetoothAdapter get");
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null) {
            sendStatus(false, "CHECK_BT_ADAPTER", "BluetoothAdapter == null (no soportado)");
            stopSelf();
            return;
        }

        // Android 12+: permisos obligatorios en tiempo de ejecución
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED
                    || ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                sendStatus(false, "PERMISSION", "Faltan BLUETOOTH_SCAN/CONNECT");
                stopSelf();
                return;
            }
        }

        scanner = adapter.getBluetoothLeScanner();
        if (scanner == null) {
            sendStatus(false, "GET_SCANNER", "BluetoothLeScanner == null");
            stopSelf();
            return;
        }
        sendStatus(true, "GET_SCANNER", "BluetoothLeScanner OK");

        ScanSettings settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_POWER)
                .build();

        try {
            List<ScanFilter> filters = new ArrayList<>();
            filters.add(new ScanFilter.Builder().setDeviceName(TARGET_DEVICE_NAME).build());
            scanner.startScan(filters, settings, callback);
            sendStatus(true, "START_SCAN", "startScan() invocado");
            Log.i(TAG, "startScan() llamado");
        } catch (Throwable t) {
            sendStatus(false, "START_SCAN", "Error startScan: " + t.getMessage());
            Log.e(TAG, "startScan failed", t);
            stopSelf();
        }
    }

    // Callback del escaneo BLE
    private final ScanCallback callback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            mostrarInformacionDispositivoBTLE(result);
        }

        @Override
        public void onScanFailed(int errorCode) {
            sendStatus(false, "SCAN_FAILED", "errorCode=" + errorCode);
            Log.e(TAG, "Scan failed: " + errorCode);
            stopSelf();
        }
    };

    /**
     * Muestra por Log información del beacon detectado (iBeacon incluido).
     */
    private void mostrarInformacionDispositivoBTLE(ScanResult resultado) {
        BluetoothDevice bluetoothDevice = resultado.getDevice();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT)
                    != PackageManager.PERMISSION_GRANTED) {
                Log.w(TAG, "Falta BLUETOOTH_CONNECT, se omiten campos de identidad.");
            } else {
                Log.d(ETIQUETA_LOG, " nombre = " + bluetoothDevice.getName());
                Log.d(ETIQUETA_LOG, " dirección = " + bluetoothDevice.getAddress());
            }
        } else {
            Log.d(ETIQUETA_LOG, " nombre = " + bluetoothDevice.getName());
            Log.d(ETIQUETA_LOG, " dirección = " + bluetoothDevice.getAddress());
        }

        byte[] bytes = (resultado.getScanRecord() != null) ? resultado.getScanRecord().getBytes() : new byte[0];
        int rssi = resultado.getRssi();

        Log.d(ETIQUETA_LOG, " ***** DISPOSITIVO DETECTADO BTLE ***** ");
        Log.d(ETIQUETA_LOG, " rssi = " + rssi);
        Log.d(ETIQUETA_LOG, " bytes (" + bytes.length + ") = " + Utilidades.bytesToHexString(bytes));

        try {
            TramaIBeacon tib = new TramaIBeacon(bytes);
            Log.d(ETIQUETA_LOG, " -------- iBeacon --------");
            Log.d(ETIQUETA_LOG, " UUID = " + Utilidades.bytesToString(tib.getUUID()));
            Log.d(ETIQUETA_LOG, " major = " + Utilidades.bytesToInt(tib.getMajor()));
            Log.d(ETIQUETA_LOG, " minor = " + Utilidades.bytesToInt(tib.getMinor()));
            Log.d(ETIQUETA_LOG, " txPower = " + tib.getTxPower());
        } catch (Throwable ignore) { }
    }

    /**
     * Detiene el escaneo de forma segura.
     */
    private void stopScan() {
        if (scanner != null) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN)
                            != PackageManager.PERMISSION_GRANTED) {
                        Log.w(TAG, "stopScan: falta permiso BLUETOOTH_SCAN");
                        return;
                    }
                }
                scanner.stopScan(callback);
                Log.i(TAG, "stopScan() llamado");
            } catch (Exception e) {
                Log.e(TAG, "Error al detener escaneo", e);
            } finally {
                scanner = null;
            }
        }
    }

    /**
     * Crea canal de notificación (Android O+)
     */
    private void ensureChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null && nm.getNotificationChannel(PermisosHelper.CHANNEL_ID) == null) {
                NotificationChannel ch = new NotificationChannel(
                        PermisosHelper.CHANNEL_ID,
                        "Beacon Scan",
                        NotificationManager.IMPORTANCE_LOW
                );
                ch.setDescription("Escaneo de beacons BLE");
                nm.createNotificationChannel(ch);
                Log.i(TAG, "Canal creado: " + PermisosHelper.CHANNEL_ID);
            }
        }
    }

    private void sendStatus(boolean ok, String step, String msg) {
        Intent i = new Intent(ACTION_STATUS);
        i.putExtra(EXTRA_OK, ok);
        i.putExtra(EXTRA_STEP, step);
        i.putExtra(EXTRA_MSG, msg);
        sendBroadcast(i);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopScan();
        stopForeground(true);
        Log.i(TAG, "Service onDestroy()");
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
