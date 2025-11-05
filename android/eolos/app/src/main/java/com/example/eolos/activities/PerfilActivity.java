package com.example.eolos.activities;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.PerfilFake;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/**
 * Autor: JINWEI
 * Fecha: 2025
 * Descripción:
 *  - Carga los datos del usuario desde el backend (GET /api/v1/perfil, JWT).
 *  - Permite editar y guardar con PUT /api/v1/perfil (JWT).
 *  - Si falla o no hay token válido, usa datos locales de ejemplo.
 */
public class PerfilActivity extends AppCompatActivity {

    private static final String TAG = "PerfilActivity";

    // Referencias UI
    private EditText etNombre, etCorreo, etTarjeta, etContrasena, etFecha;
    private Button btnGuardar, btnVolver;

    private final SimpleDateFormat dateFormat = new SimpleDateFormat("d/M/yyyy", Locale.getDefault());
    private PerfilFake perfil;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        // 1) Vincular vistas
        etNombre = findViewById(R.id.etNombre);
        etCorreo = findViewById(R.id.etCorreo);
        etTarjeta = findViewById(R.id.etTarjeta);
        etContrasena = findViewById(R.id.etContrasena);
        etFecha = findViewById(R.id.etFecha);
        btnGuardar = findViewById(R.id.btnGuardar);
        btnVolver = findViewById(R.id.btnVolver);

        // 2) Selector de fecha (solo para mostrar/editar texto)
        etFecha.setInputType(InputType.TYPE_NULL);
        etFecha.setOnClickListener(v -> showDatePicker());

        // 3) Cargar perfil desde servidor (o ejemplo local si no hay token/red)
        cargarPerfil();

        // 4) Guardar cambios
        btnGuardar.setOnClickListener(v -> {
            if (!validateInputs()) return;

            if (perfil == null) perfil = new PerfilFake(this); // fallback
            perfil.setNombre(s(etNombre.getText()));
            perfil.setCorreo(s(etCorreo.getText()));
            perfil.setTarjeta(s(etTarjeta.getText()));
            perfil.setContrasena(s(etContrasena.getText()));
            perfil.setFechaRegistro(s(etFecha.getText()));

            setEnabled(false);
            Toast.makeText(this, "Guardando perfil...", Toast.LENGTH_SHORT).show();

            perfil.guardarPerfil((exito, codigo, cuerpo) -> runOnUiThread(() -> {
                setEnabled(true);
                if (exito) {
                    Toast.makeText(this, "✅ Guardado correctamente", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(this, "❌ Error al guardar (" + codigo + ")", Toast.LENGTH_SHORT).show();
                    Log.w(TAG, "PUT /perfil fallo: code=" + codigo + ", body=" + cuerpo);
                }
            }));
        });

        // 5) Volver
        btnVolver.setOnClickListener(v -> finish());
    }

    private void cargarPerfil() {
        setEnabled(false);

        perfil = new PerfilFake(this, (p, desdeServidor) -> runOnUiThread(() -> {
            setEnabled(true);
            perfil = p;
            rellenarUI(perfil);
            Toast.makeText(this,
                    desdeServidor ? "Perfil cargado desde el servidor"
                            : "No hay token o conexión. Usando datos locales.",
                    Toast.LENGTH_SHORT).show();
        }));
    }

    /** Rellenar UI con los datos actuales */
    private void rellenarUI(PerfilFake p) {
        if (p == null) return;
        etNombre.setText(nv(p.getNombre()));
        etCorreo.setText(nv(p.getCorreo()));
        etTarjeta.setText(nv(p.getTarjeta()));
        etContrasena.setText(nv(p.getContrasena()));
        etFecha.setText(nv(p.getFechaRegistro()));
    }

    /** Validaciones básicas */
    private boolean validateInputs() {
        String nombre = s(etNombre.getText());
        String correo = s(etCorreo.getText());
        String tarjeta = s(etTarjeta.getText());
        String fecha = s(etFecha.getText());

        if (nombre.isEmpty()) { etNombre.setError("Campo requerido"); etNombre.requestFocus(); return false; }
        if (correo.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            etCorreo.setError("Correo inválido"); etCorreo.requestFocus(); return false; }
        if (tarjeta.isEmpty()) { etTarjeta.setError("Campo requerido"); etTarjeta.requestFocus(); return false; }
        if (fecha.isEmpty()) { etFecha.setError("Campo requerido"); etFecha.requestFocus(); return false; }
        return true;
    }

    /** Muestra DatePicker y vuelca fecha formateada */
    private void showDatePicker() {
        final Calendar cal = Calendar.getInstance();
        try {
            String txt = s(etFecha.getText());
            if (!txt.isEmpty()) {
                java.util.Date d = dateFormat.parse(txt);
                if (d != null) cal.setTime(d);
            }
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

    /** Habilitar/Deshabilitar controles de la pantalla */
    private void setEnabled(boolean enabled) {
        btnGuardar.setEnabled(enabled);
        btnVolver.setEnabled(enabled);
        etNombre.setEnabled(enabled);
        etCorreo.setEnabled(enabled);
        etTarjeta.setEnabled(enabled);
        etContrasena.setEnabled(enabled);
        etFecha.setEnabled(enabled);
    }

    // ==== Utilidades de strings ====
    private String s(CharSequence cs) { return cs == null ? "" : cs.toString().trim(); }
    private String nv(String s) { return s == null ? "" : s; }
}
