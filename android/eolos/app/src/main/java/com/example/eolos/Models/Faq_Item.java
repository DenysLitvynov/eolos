package com.example.eolos.Models;

public class Faq_Item {
    private String pregunta;
    private String respuesta;
    private boolean expandido;

    public Faq_Item(String pregunta, String respuesta) {
        this.pregunta = pregunta;
        this.respuesta = respuesta;
        this.expandido = false; // por defecto, colapsado
    }

    public String getPregunta() {
        return pregunta;
    }

    public String getRespuesta() {
        return respuesta;
    }

    public boolean isExpandido() {
        return expandido;
    }

    public void setExpandido(boolean expandido) {
        this.expandido = expandido;
    }
}