// com/example/eolos/data/PerfilDto.java
package com.example.eolos.data;

public class PerfilDto {
    public String nombre;
    public String correo;
    public String tarjeta;
    public String contrasena;
    public String fecha; // "d/M/yyyy"

    public PerfilDto() {}

    public PerfilDto(String nombre, String correo, String tarjeta, String contrasena, String fecha) {
        this.nombre = nombre;
        this.correo = correo;
        this.tarjeta = tarjeta;
        this.contrasena = contrasena;
        this.fecha = fecha;
    }
}
