package com.example.eolos.Models;

public class Recompensa_Item {

    private int logoResId;
    private String titulo;
    private  Double crit_num_km;

    public Recompensa_Item(int logoResId, String titulo, double crit_num_km) {
        this.logoResId = logoResId;
        this.titulo = titulo;
        this.crit_num_km= crit_num_km;
    }

    public int getLogoResId() {
        return logoResId;
    }

    public String getTitulo() {
        return titulo;
    }

    public double get_Crit_num_km() {
        return crit_num_km;
    }

}