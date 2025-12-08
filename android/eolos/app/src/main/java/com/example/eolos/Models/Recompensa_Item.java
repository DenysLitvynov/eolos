package com.example.eolos.Models;

public class Recompensa_Item {

    private int logoResId;
    private String titulo;

    public Recompensa_Item(int logoResId, String titulo) {
        this.logoResId = logoResId;
        this.titulo = titulo;
    }

    public int getLogoResId() {
        return logoResId;
    }

    public String getTitulo() {
        return titulo;
    }
}