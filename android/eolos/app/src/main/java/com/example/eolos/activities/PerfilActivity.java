package com.example.eolos.activities;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.PerfilFake;
import com.google.android.material.button.MaterialButton;

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

    private final SimpleDateFormat dateFormat =
            new SimpleDateFormat("d/M/yyyy", Locale.getDefault());

    private PerfilFake perfil;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);




        setupBottomNavigation();    // Configura la barra de navegación inferior


        // Verificar token
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        Button logoutButton = findViewById(R.id.logoutButton);


        logoutButton.setOnClickListener(v -> {
            prefs.edit().remove("token").apply();
            Toast.makeText(this, "Sesión cerrada", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, MainActivity.class));
            finish();
        });




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

            if (perfil == null) perfil = new PerfilFake(this); // fallback local
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
        btnVolver.setOnClickListener(v -> {
            rellenarUI(perfil);  // 恢复原数据
            Toast.makeText(this, "Cambios descartados", Toast.LENGTH_SHORT).show();
        });
    }

    private void setupBottomNavigation() {

        // Recuperamos cada icono directamente por su ID real del XML
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        // Listeners según tu lógica original
        iconInicio.setOnClickListener(v ->
                startActivity(new Intent(this, HomeActivity.class)));

        iconMapa.setOnClickListener(v ->
                Toast.makeText(this, "Mapa", Toast.LENGTH_SHORT).show());

        iconQR.setOnClickListener(v ->
                startActivity(new Intent(this, ConnectionActivity.class)));

        iconAlertas.setOnClickListener(v ->
                Toast.makeText(this, "Alertas", Toast.LENGTH_SHORT).show());

        iconPerfil.setOnClickListener(v ->
                startActivity(new Intent(this, PerfilActivity.class)));
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
        etTarjeta.setText(nv(p.getTarjeta()));          // puede estar vacío
        etContrasena.setText(nv(p.getContrasena()));    // normalmente no viene del servidor
        etFecha.setText(nv(p.getFechaRegistro()));
    }

    /** Validaciones básicas */
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
            etCorreo.setError("Correo inválido");
            etCorreo.requestFocus();
            return false;
        }

        // tarjeta: OPCIONAL，但如果填了，可以做一些简单校验（长度 <= 9）
        if (!tarjeta.isEmpty() && tarjeta.length() > 9) {
            etTarjeta.setError("Máximo 9 caracteres");
            etTarjeta.requestFocus();
            return false;
        }

        // fecha：可选，不强制
        // 如果你想强制要求日期，可以取消下面注释
        /*
        if (fecha.isEmpty()) {
            etFecha.setError("Campo requerido");
            etFecha.requestFocus();
            return false;
        }
        */

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
    private String s(CharSequence cs) {
        return cs == null ? "" : cs.toString().trim();
    }

    private String nv(String s) {
        return s == null ? "" : s;
    }



}
