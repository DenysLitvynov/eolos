/**
 * Fichero: PeticionarioREST.java
 * Descripción: Clase que gestiona peticiones REST en segundo plano usando AsyncTask.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 25/09/2025
 */

package com.example.eolos;

import android.os.AsyncTask;
import android.util.Log;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
public class PeticionarioREST extends AsyncTask<Void, Void, Boolean> {

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    private String elMetodo;
    private String urlDestino;
    private String elCuerpo = null;
    private RespuestaREST laRespuesta;
    private int codigoRespuesta;
    private String cuerpoRespuesta = "";

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    public PeticionarioREST() {
        Log.d("clienterestandroid", "constructor()");
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    /**
     * Inicializa la petición REST con los parámetros y ejecuta el AsyncTask.
     *
     * @param metodo Método HTTP ("GET", "POST", "PUT", ...)
     * @param urlDestino URL a la que se envía la petición
     * @param cuerpo JSON u otro cuerpo a enviar (puede ser null)
     * @param laRespuesta Objeto que recibe la respuesta vía callback
     */
    public void hacerPeticionREST(String metodo, String urlDestino, String cuerpo, RespuestaREST laRespuesta) {
        this.elMetodo = metodo;
        this.urlDestino = urlDestino;
        this.elCuerpo = cuerpo;
        this.laRespuesta = laRespuesta;

        this.execute(); // otro thread ejecutará doInBackground()
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    /**
     * Envía la petición HTTP en segundo plano y obtiene la respuesta.
     *
     * @param params No se usa (AsyncTask requiere Void...)
     * @return true si la petición se completó correctamente, false si hubo error
     */
    @Override
    protected Boolean doInBackground(Void... params) {
        Log.d("clienterestandroid", "doInBackground()");

        try {
            // envio la petición

            Log.d("clienterestandroid", "doInBackground() me conecto a >" + urlDestino + "<");

            URL url = new URL(urlDestino);

            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestProperty("Content-Type", "application/json; charset-utf-8");
            connection.setRequestMethod(this.elMetodo);
            // connection.setRequestProperty("Accept", "*/*);

            // connection.setUseCaches(false);
            connection.setDoInput(true);

            if (!this.elMetodo.equals("GET") && this.elCuerpo != null) {
                Log.d("clienterestandroid", "doInBackground(): no es get, pongo cuerpo");
                connection.setDoOutput(true);
                // si no es GET, pongo el cuerpo que me den en la peticin
                DataOutputStream dos = new DataOutputStream(connection.getOutputStream());
                dos.writeBytes(this.elCuerpo);
                dos.flush();
                dos.close();
            }

            // ya he enviado la peticin
            Log.d("clienterestandroid", "doInBackground(): peticin enviada ");

            // ahora obtengo la respuesta

            int rc = connection.getResponseCode();
            String rm = connection.getResponseMessage();
            String respuesta = "" + rc + " : " + rm;
            Log.d("clienterestandroid", "doInBackground() recibo respuesta = " + respuesta);
            this.codigoRespuesta = rc;

            try {

                InputStream is = connection.getInputStream();
                BufferedReader br = new BufferedReader(new InputStreamReader(is));

                Log.d("clienterestandroid", "leyendo cuerpo");
                StringBuilder acumulador = new StringBuilder();
                String linea;
                while ((linea = br.readLine()) != null) {
                    Log.d("clienterestandroid", linea);
                    acumulador.append(linea);
                }
                Log.d("clienterestandroid", "FIN leyendo cuerpo");

                this.cuerpoRespuesta = acumulador.toString();
                Log.d("clienterestandroid", "cuerpo recibido=" + this.cuerpoRespuesta);

                connection.disconnect();

            } catch (IOException ex) {
                // dispara excepcin cuando la respuesta REST no tiene cuerpo y yo intento getInputStream()
                Log.d("clienterestandroid", "doInBackground() : parece que no hay cuerpo en la respuesta");
            }

            return true; // doInBackground() termina bien

        } catch (Exception ex) {
            Log.d("clienterestandroid", "doInBackground(): ocurrio alguna otra excepcion: " + ex.getMessage());
        }

        return false; // doInBackground() NO termina bien
    } // ()

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    /**
     * Llama al callback con el resultado de la petición tras terminar doInBackground.
     *
     * @param comoFue true si doInBackground terminó bien, false si hubo error
     */
    protected void onPostExecute(Boolean comoFue) {
        // llamado tras doInBackground()
        Log.d("clienterestandroid", "onPostExecute() comoFue = " + comoFue);
        this.laRespuesta.callback(this.codigoRespuesta, this.cuerpoRespuesta);
    }

    // --------------------------------------------------------------------
    // --------------------------------------------------------------------
    public interface RespuestaREST {
        void callback(int codigo, String cuerpo);
    }

}  // class

// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------


