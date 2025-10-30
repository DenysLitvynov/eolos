/**
 * Fichero: PermisorsHelper.java
 * Descripción: Verificar y solicitar los permisos necesarios.
 * Autor: JINWEI
 * Fecha: 30/10/2025
 */



package com.example.eolos.servicio;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.BluetoothLeScanner;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.LocationManager;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;

import java.util.ArrayList;
import java.util.List;

public class PermisosHelper {

    private static final String TAG = "PermsHelper";
    private static final int REQ_ENABLE_BT       = 3002;  // Código para activar Bluetooth
    private static final int REQ_ENABLE_LOCATION = 3004;  // Código para activar ubicación
    private static final int REQ_PERMS_CHAIN     = 3100;  // Código para solicitud de permisos en cadena

    public static final String CHANNEL_ID = "beacon_scan_channel";

    /**
     * Punto de entrada principal:
     * Llamar a este método desde una Activity para verificar permisos y arrancar el servicio BLE.
     */
    public static void verificarYIniciarServicio(Activity activity) {
        // Crear el canal de notificaciones si no existe
        ensureNotificationChannelExists(activity);

        // 1️⃣ Verificar y solicitar permisos necesarios
        if (!ensureBluetoothRuntimePerms(activity)) return;
        if (!ensureNotificationPermission(activity)) return;
        if (!ensureLocationPermission(activity)) return;

        // 2️⃣ Verificar que Bluetooth y ubicación estén activados
        if (!ensureBluetoothSwitch(activity)) return;
        if (!ensureBluetoothReadySoft(activity)) return;
        if (!isLocationEnabled(activity)) {
            Toast.makeText(activity, "Activa el servicio de ubicación", Toast.LENGTH_SHORT).show();
            promptEnableLocationService(activity);
            return;
        }

        // 3️⃣ Si todo está correcto, iniciar el servicio de escaneo BLE
        Intent serviceIntent = new Intent(activity, BeaconScanService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // Para Android 8.0 o superior, los servicios deben iniciarse en primer plano
            ContextCompat.startForegroundService(activity, serviceIntent);
        } else {
            activity.startService(serviceIntent);
        }
        Toast.makeText(activity, "Escaneo BLE iniciado en segundo plano", Toast.LENGTH_SHORT).show();
        Log.i(TAG, "BeaconScanService iniciado (todos los permisos OK)");
    }

    // ————————————————————————————————
    //     MÉTODOS DE VERIFICACIÓN DE PERMISOS Y ESTADOS
    // ————————————————————————————————

    /**
     * Verifica y solicita permisos de Bluetooth (Android 12+).
     */
    private static boolean ensureBluetoothRuntimePerms(Activity a) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return true;
        List<String> req = new ArrayList<>();
        if (!hasPerm(a, Manifest.permission.BLUETOOTH_SCAN))    req.add(Manifest.permission.BLUETOOTH_SCAN);
        if (!hasPerm(a, Manifest.permission.BLUETOOTH_CONNECT)) req.add(Manifest.permission.BLUETOOTH_CONNECT);
        if (!req.isEmpty()) {
            ActivityCompat.requestPermissions(a, req.toArray(new String[0]), REQ_PERMS_CHAIN);
            return false;
        }
        return true;
    }

    /**
     * Verifica si el Bluetooth está activado y, si no lo está, solicita al usuario que lo active.
     */
    @SuppressLint("MissingPermission")
    private static boolean ensureBluetoothSwitch(Activity a) {
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null) {
            Toast.makeText(a, "Este dispositivo no soporta Bluetooth.", Toast.LENGTH_SHORT).show();
            return false;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                !hasPerm(a, Manifest.permission.BLUETOOTH_CONNECT)) {
            // En Android 12+ se necesita el permiso CONNECT para leer el estado del Bluetooth
            ActivityCompat.requestPermissions(a,
                    new String[]{Manifest.permission.BLUETOOTH_CONNECT}, REQ_PERMS_CHAIN);
            return false;
        }
        if (!adapter.isEnabled()) {
            try {
                a.startActivityForResult(new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE), REQ_ENABLE_BT);
            } catch (Exception e) { Log.w(TAG, "No se pudo solicitar activar BT", e); }
            return false;
        }
        return true;
    }

    /**
     * Verifica y solicita el permiso para mostrar notificaciones (Android 13+).
     */
    private static boolean ensureNotificationPermission(Activity a) {
        if (Build.VERSION.SDK_INT < 33) return true;
        if (hasPerm(a, Manifest.permission.POST_NOTIFICATIONS)) return true;
        ActivityCompat.requestPermissions(a,
                new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_PERMS_CHAIN);
        return false;
    }

    /**
     * Verifica y solicita el permiso de ubicación, necesario para el escaneo BLE.
     */
    private static boolean ensureLocationPermission(Activity a) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) return true;
        if (hasPerm(a, Manifest.permission.ACCESS_FINE_LOCATION)) return true;
        ActivityCompat.requestPermissions(a,
                new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, REQ_PERMS_CHAIN);
        return false;
    }

    // ————————————————————————————————
    //     MÉTODOS DE PUENTE PARA CALLBACKS
    // ————————————————————————————————

    /**
     * Llamar desde onRequestPermissionsResult() en la Activity
     * para continuar el flujo después de conceder permisos.
     */
    public static void onRequestPermissionsResult(Activity a, int requestCode) {
        if (requestCode == REQ_PERMS_CHAIN) {
            // El usuario ya gestionó los permisos → reintentar
            verificarYIniciarServicio(a);
        }
    }

    /**
     * Llamar desde onActivityResult() en la Activity
     * después de que el usuario haya activado Bluetooth o ubicación.
     */
    public static void onActivityResult(Activity a, int requestCode, int resultCode, Intent data) {
        if (requestCode == REQ_ENABLE_BT || requestCode == REQ_ENABLE_LOCATION) {
            verificarYIniciarServicio(a);
        }
    }

    // ————————————————————————————————
    //     MÉTODOS AUXILIARES / UTILITARIOS
    // ————————————————————————————————

    /** Comprueba si el permiso indicado está concedido. */
    private static boolean hasPerm(Context c, String perm) {
        return ContextCompat.checkSelfPermission(c, perm) == PackageManager.PERMISSION_GRANTED;
    }

    /** Verifica si el Bluetooth está preparado para escanear (tiene adaptador y escáner BLE disponible). */
    private static boolean ensureBluetoothReadySoft(Context c) {
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null) return false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                !hasPerm(c, Manifest.permission.BLUETOOTH_CONNECT)) return false;
        if (!adapter.isEnabled()) return false;
        BluetoothLeScanner scanner = adapter.getBluetoothLeScanner();
        return scanner != null;
    }

    /** Comprueba si los servicios de ubicación del sistema están activados. */
    private static boolean isLocationEnabled(Context c) {
        LocationManager lm = (LocationManager) c.getSystemService(Context.LOCATION_SERVICE);
        if (lm == null) return false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) return lm.isLocationEnabled();
        try {
            return lm.isProviderEnabled(LocationManager.GPS_PROVIDER)
                    || lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
        } catch (Exception e) { return false; }
    }

    /** Abre la pantalla de ajustes para que el usuario active la ubicación. */
    private static void promptEnableLocationService(Activity a) {
        try {
            a.startActivityForResult(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS), REQ_ENABLE_LOCATION);
        } catch (Exception e) { Log.w(TAG, "No se pudieron abrir los ajustes de ubicación", e); }
    }

    /** Crea el canal de notificaciones necesario para los servicios en primer plano (Android 8.0+). */
    private static void ensureNotificationChannelExists(Context c) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null && nm.getNotificationChannel(CHANNEL_ID) == null) {
                NotificationChannel ch = new NotificationChannel(
                        CHANNEL_ID, "Beacon Scan", NotificationManager.IMPORTANCE_LOW);
                ch.setDescription("Escaneo de balizas BLE");
                nm.createNotificationChannel(ch);
            }
        }
    }

}
