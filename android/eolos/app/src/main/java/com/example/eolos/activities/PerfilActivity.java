// com/example/eolos/activities/PerfilActivity.java
package com.example.eolos.activities;

import android.app.DatePickerDialog;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.util.Base64;
import android.util.Log;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.PeticionarioREST;
import com.example.eolos.R;
import com.example.eolos.logica_fake.PerfilFake;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/**
 * Clase: PerfilActivity
 * Descripción:
 *  - Pantalla para mostrar y editar el perfil del usuario.
 *  - Al iniciar, intenta obtener los datos del servidor usando el correo extraído del token JWT.
 *  - Si falla la conexión o el token no contiene correo, usa un perfil de ejemplo local (PerfilFake).
 *  - Permite guardar cambios mediante una petición POST.
 *
 * Autor: JINWEI
 * Fecha: 2025
 */
public class PerfilActivity extends AppCompatActivity {

    private static final String TAG = "PerfilActivity";

    // ================== Referencias UI ==================
    private EditText etNombre, etCorreo, etTarjeta, etContrasena, etFecha;
    private Button btnGuardar, btnVolver;

    private final SimpleDateFormat dateFormat = new SimpleDateFormat("d/M/yyyy", Locale.getDefault());
    private PerfilFake perfil;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        // 1) Vincular elementos UI
        etNombre = findViewById(R.id.etNombre);
        etCorreo = findViewById(R.id.etCorreo);
        etTarjeta = findViewById(R.id.etTarjeta);
        etContrasena = findViewById(R.id.etContrasena);
        etFecha = findViewById(R.id.etFecha);
        btnGuardar = findViewById(R.id.btnGuardar);
        btnVolver = findViewById(R.id.btnVolver);

        // 2) Configurar selector de fecha (evita mostrar teclado)
        etFecha.setInputType(InputType.TYPE_NULL);
        etFecha.setOnClickListener(v -> showDatePicker());

        // 3) Al iniciar: obtener el perfil desde el servidor usando el token JWT.
        //    Si falla o no hay token válido → carga datos de ejemplo.
        cargarPerfilPreferServidorUsandoToken();

        // 4) Acción "Guardar": envía los datos del formulario con POST.
        btnGuardar.setOnClickListener(v -> {
            if (!validateInputs()) return;

            if (perfil == null) perfil = new PerfilFake();
            perfil.setNombre(s(etNombre.getText()));
            perfil.setCorreo(s(etCorreo.getText()));
            perfil.setTarjeta(s(etTarjeta.getText()));
            perfil.setContrasena(s(etContrasena.getText()));
            perfil.setFechaRegistro(s(etFecha.getText()));

            Toast.makeText(this, "Guardando perfil...", Toast.LENGTH_SHORT).show();
            perfil.guardarPerfil();
        });

        // 5) Botón "Volver": regresa a la pantalla anterior
        btnVolver.setOnClickListener(v -> finish());
    }

    /**
     * Método principal: intenta obtener el correo desde el token JWT almacenado en SharedPreferences.
     * Si se obtiene un correo válido, solicita los datos del perfil desde el servidor.
     * Si no hay token o el correo no se puede extraer, carga un perfil de ejemplo local.
     */
    private void cargarPerfilPreferServidorUsandoToken() {
        setEnabled(false);

        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);

        String correo = extraerEmailDeJWT(token); // Puede devolver vacío si el token no tiene correo
        Log.d(TAG, "Correo extraído del token = " + correo);

        if (!correo.isEmpty() && Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            // Si el correo es válido → intenta obtener los datos desde el servidor
            perfil = new PerfilFake(correo, (p, desdeServidor) -> runOnUiThread(() -> {
                setEnabled(true);
                perfil = p;
                rellenarUI(perfil);
                Toast.makeText(this,
                        desdeServidor ? "Perfil cargado desde el servidor"
                                : "Sin datos en servidor, usando ejemplo local",
                        Toast.LENGTH_SHORT).show();
            }));
        } else {
            // Si no se puede obtener correo → usa perfil local de ejemplo
            perfil = new PerfilFake();
            rellenarUI(perfil);
            setEnabled(true);
            Toast.makeText(this, "Token sin correo. Cargando ejemplo local.", Toast.LENGTH_SHORT).show();
        }
    }

    /**
     * Extrae el correo electrónico de un token JWT.
     * Busca en los campos comunes del payload: "email", "sub", "preferred_username".
     * Si no encuentra ninguno válido, devuelve cadena vacía.
     */
    private String extraerEmailDeJWT(String jwt) {
        if (jwt == null || jwt.trim().isEmpty()) return "";
        try {
            String[] parts = jwt.split("\\.");
            if (parts.length < 2) return "";

            // El segundo segmento del JWT es el "payload", codificado en Base64 URL-safe
            byte[] decoded = Base64.decode(parts[1], Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
            String json = new String(decoded, StandardCharsets.UTF_8);
            JSONObject o = new JSONObject(json);

            // Prioridad: email → sub → preferred_username
            String email = o.optString("email", "");
            if (!email.isEmpty()) return email;

            String sub = o.optString("sub", "");
            if (!sub.isEmpty() && Patterns.EMAIL_ADDRESS.matcher(sub).matches()) return sub;

            String preferred = o.optString("preferred_username", "");
            if (!preferred.isEmpty() && Patterns.EMAIL_ADDRESS.matcher(preferred).matches()) return preferred;

            return "";
        } catch (Exception e) {
            Log.e(TAG, "Error al parsear JWT: " + e.getMessage());
            return "";
        }
    }

    /** Rellena los campos del formulario con los datos del perfil cargado */
    private void rellenarUI(PerfilFake p) {
        if (p == null) return;
        etNombre.setText(nv(p.getNombre()));
        etCorreo.setText(nv(p.getCorreo()));
        etTarjeta.setText(nv(p.getTarjeta()));
        etContrasena.setText(nv(p.getContrasena()));
        etFecha.setText(nv(p.getFechaRegistro()));
    }

    /** Validaciones básicas de los campos antes de guardar */
    private boolean validateInputs() {
        String nombre = s(etNombre.getText());
        String correo = s(etCorreo.getText());
        String tarjeta = s(etTarjeta.getText());
        String fecha = s(etFecha.getText());

        if (nombre.isEmpty()) {
            etNombre.setError("Campo requerido");
            etNombre.requestFocus();
            return false;
        }
        if (correo.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            etCorreo.setError("Correo electrónico inválido");
            etCorreo.requestFocus();
            return false;
        }
        if (tarjeta.isEmpty()) {
            etTarjeta.setError("Campo requerido");
            etTarjeta.requestFocus();
            return false;
        }
        if (fecha.isEmpty()) {
            etFecha.setError("Campo requerido");
            etFecha.requestFocus();
            return false;
        }
        return true;
    }

    /** Muestra un selector de fecha (DatePickerDialog) y actualiza el campo de texto */
    private void showDatePicker() {
        final Calendar cal = Calendar.getInstance();
        try {
            String txt = s(etFecha.getText());
            if (!txt.isEmpty()) cal.setTime(dateFormat.parse(txt));
        } catch (ParseException ignored) {}

        new DatePickerDialog(
                this,
                (view, year, month, dayOfMonth) -> {
                    cal.set(Calendar.YEAR, year);
                    cal.set(Calendar.MONTH, month);
                    cal.set(Calendar.DAY_OF_MONTH, dayOfMonth);
                    etFecha.setText(dateFormat.format(cal.getTime()));
                },
                cal.get(Calendar.YEAR),
                cal.get(Calendar.MONTH),
                cal.get(Calendar.DAY_OF_MONTH)
        ).show();
    }

    /** Habilita o deshabilita los controles de la interfaz */
    private void setEnabled(boolean enabled) {
        btnGuardar.setEnabled(enabled);
        btnVolver.setEnabled(enabled);
        etNombre.setEnabled(enabled);
        etCorreo.setEnabled(enabled);
        etTarjeta.setEnabled(enabled);
        etContrasena.setEnabled(enabled);
        etFecha.setEnabled(enabled);
    }

    // Utilidades para manejo seguro de strings
    private String s(CharSequence cs) { return cs == null ? "" : cs.toString().trim(); }
    private String nv(String s) { return s == null ? "" : s; }
}
