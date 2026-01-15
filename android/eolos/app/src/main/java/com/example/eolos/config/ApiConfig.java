package com.example.eolos.config;

public class ApiConfig {
    // CAMBIAR ESTA IP POR LA QUE CORRESPONDA (donde corre uvicorn)
    public static final String BASE_URL = "http://192.168.1.149:8000";
    
    public static final String ENDPOINT_PERFIL = BASE_URL + "/api/v1/perfil";
    public static final String ENDPOINT_TRAYECTOS_ULTIMO = BASE_URL + "/api/v1/trayectos/usuario/ultimo";
    public static final String ENDPOINT_TRAYECTOS_ULTIMOS = BASE_URL + "/api/v1/trayectos/usuario/ultimos";
    public static final String ENDPOINT_TRAYECTO_MEDICIONES = BASE_URL + "/api/v1/trayectos/%s/mediciones";
}
