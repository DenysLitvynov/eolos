/**
 * Archivo: PerfilFake.java
 * Descripción: Clase auxiliar que simula un perfil de usuario fijo.
 *              Se usa cuando no hay conexión con el servidor.
 * Autor: JINWEI
 * Fecha: 31/10/2025
 */
package com.example.eolos.logica_fake;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class PerfilFake {

    // Campos del perfil falso
    private String nombre;
    private String correo;
    private String tarjeta;
    private String contrasena;
    private String fechaRegistro;

    /**
     * Constructor por defecto: carga un perfil de demostración.
     */
    public PerfilFake() {
        cargarPerfilEjemplo();
    }

    /**
     * Carga un único perfil de ejemplo (sin aleatoriedad).
     * Se utiliza cuando no hay datos locales ni conexión.
     */
    private void cargarPerfilEjemplo() {
        this.nombre = "María López";
        this.correo = "maria@eolos.com";
        this.tarjeta = "ABC123";
        this.contrasena = "password";
        this.fechaRegistro = new SimpleDateFormat("d/M/yyyy", Locale.getDefault()).format(new Date());
    }

    // ===================== Getters =====================
    public String getNombre() { return nombre; }
    public String getCorreo() { return correo; }
    public String getTarjeta() { return tarjeta; }
    public String getContrasena() { return contrasena; }
    public String getFechaRegistro() { return fechaRegistro; }

    // ===================== Setters =====================
    public void setNombre(String nombre) { this.nombre = nombre; }
    public void setCorreo(String correo) { this.correo = correo; }
    public void setTarjeta(String tarjeta) { this.tarjeta = tarjeta; }
    public void setContrasena(String contrasena) { this.contrasena = contrasena; }
    public void setFechaRegistro(String fechaRegistro) { this.fechaRegistro = fechaRegistro; }

    @Override
    public String toString() {
        return "PerfilFake{" +
                "nombre='" + nombre + '\'' +
                ", correo='" + correo + '\'' +
                ", tarjeta='" + tarjeta + '\'' +
                ", contrasena='" + contrasena + '\'' +
                ", fechaRegistro='" + fechaRegistro + '\'' +
                '}';
    }
}
