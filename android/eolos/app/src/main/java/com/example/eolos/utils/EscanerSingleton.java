/**
 * Fichero: EscanerSingleton.java
 * Descripción: Clase Singleton que garantiza una única instancia del escáner BLE (EscanerIBeacons)
 *              en toda la aplicación. Permite centralizar el control del escaneo y compartir
 *              el estado de conexión entre distintas actividades o fragmentos.
 * Autor: Hugo Belda
 * Fecha: 29/10/2025
 */
package com.example.eolos.utils;

import com.example.eolos.EscanerIBeacons;

public class EscanerSingleton {

    private static EscanerSingleton instance;
    private EscanerIBeacons escaner;
    public long ultimaRecepcion = 0L;

    /**
     * Constructor privado.
     * Impide que se creen instancias fuera de esta clase.
     */
    private EscanerSingleton() { }

    /**
     * Devuelve la instancia única del singleton.
     * Si no existe, la crea en el momento de la primera llamada.
     *
     * @return instancia única de EscanerSingleton
     */
    public static EscanerSingleton getInstance() {
        if (instance == null) {
            instance = new EscanerSingleton();
        }
        return instance;
    }

    /**
     * Inicia el proceso de escaneo BLE.
     * - Recibe un objeto EscanerIBeacons ya configurado.
     * - Inicializa el Bluetooth.
     * - Inicia el escaneo automático.
     * - Registra un callback para actualizar el timestamp de la última recepción.
     *
     */
    public void iniciarEscaneo(EscanerIBeacons escaner) {
        this.escaner = escaner;
        this.escaner.inicializarBlueTooth();
        this.escaner.iniciarEscaneoAutomatico("EmisoraBLE");

        // Reemplaza el escáner con una instancia que actualiza la marca de tiempo
        this.escaner = new EscanerIBeacons(escaner.context, jsonMedida -> {
            ultimaRecepcion = System.currentTimeMillis();
        });
    }

    /**
     * Devuelve el timestamp de la última recepción de señal BLE
     */
    public long getUltimaRecepcion() {
        return ultimaRecepcion;
    }

    /**
     * Devuelve el escáner BLE activo.
     */
    public EscanerIBeacons getEscaner() {
        return escaner;
    }
}
