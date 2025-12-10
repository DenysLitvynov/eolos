package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.util.Patterns;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.PerfilFake;
import com.google.android.material.button.MaterialButton;

import java.util.regex.Pattern;

/**
 * Autor: JINWEI
 * Fecha: 2025
 *
 * Pantalla de PERFIL en Android:
 *  - Carga datos del usuario (GET /api/v1/perfil, JWT).
 *  - Permite editar nombre/correo/targeta_id.
 *  - Cambia contraseña usando:
 *      - contrasena_actual (OBLIGATORIA)
 *      - contrasena_nueva (OPCIONAL, con reglas)
 *
 *  Regla de contraseña = misma que en frontend web:
 *    Mínimo 8 caracteres, debe incluir:
 *      - mayúsculas
 *      - minúsculas
 *      - números
 *      - símbolos (@$!%*?&)
 */
public class PerfilActivity extends AppCompatActivity {

    private static final String TAG = "PerfilActivity";

    // Mismo patrón que en frontend/js/scripts/perfil.js
    private static final Pattern PASS_PATTERN = Pattern.compile(
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&]).{8,}$"
    );

    // UI
    private EditText etNombre, etCorreo, etTarjeta;
    private EditText etContrasenaActual, etNuevaContrasena, etRepetirContrasena;
    private MaterialButton btnGuardar, btnVolver, btnLogout;

    private PerfilFake perfil;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        setupBottomNavigation();

        // ===== Verificar token JWT =====
        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
        String token = prefs.getString("token", null);
        if (token == null) {
            Toast.makeText(this, "No estás autenticado. Redirigiendo...", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        // ===== Botón Cerrar Sesión =====
        btnLogout = findViewById(R.id.logoutButton);
        btnLogout.setOnClickListener(v -> {
            prefs.edit().remove("token").remove("targeta_id").apply();
            Toast.makeText(this, "Sesión cerrada", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, MainActivity.class));
            finish();
        });

        // ===== Vincular vistas =====
        etNombre  = findViewById(R.id.etNombre);
        etCorreo  = findViewById(R.id.etCorreo);
        etTarjeta = findViewById(R.id.etTarjeta);

        etContrasenaActual  = findViewById(R.id.etContrasenaActual);
        etNuevaContrasena   = findViewById(R.id.etNuevaContrasena);
        etRepetirContrasena = findViewById(R.id.etRepetirContrasena);

        btnGuardar = findViewById(R.id.btnGuardar);
        btnVolver  = findViewById(R.id.btnVolver);

        // ===== Cargar perfil =====
        cargarPerfil();

        // ===== Guardar cambios =====
        btnGuardar.setOnClickListener(v -> {
            if (!validateInputs()) return;

            if (perfil == null) perfil = new PerfilFake(this);  // fallback local

            String nombre  = s(etNombre.getText());
            String correo  = s(etCorreo.getText());
            String tarjeta = s(etTarjeta.getText());
            String actual  = s(etContrasenaActual.getText());
            String nueva   = s(etNuevaContrasena.getText()); // puede estar vacío

            perfil.setNombre(nombre);
            perfil.setCorreo(correo);
            perfil.setTarjeta(tarjeta);

            // estos nuevos campos se usan para el payload del PUT
            perfil.setContrasenaActual(actual);
            perfil.setContrasenaNueva(nueva.isEmpty() ? null : nueva);

            setEnabled(false);
            Toast.makeText(this, "Guardando perfil...", Toast.LENGTH_SHORT).show();

            perfil.guardarPerfil((exito, codigo, cuerpo) -> runOnUiThread(() -> {
                setEnabled(true);
                if (exito) {
                    Toast.makeText(this, "✅ Guardado correctamente", Toast.LENGTH_SHORT).show();

                    // refrescamos targeta_id por si backend la cambia
                    String targetaActual = perfil.getTarjeta();
                    if (targetaActual != null && !targetaActual.isEmpty()) {
                        etTarjeta.setText(targetaActual);
                        Toast.makeText(this, "Targeta ID: " + targetaActual, Toast.LENGTH_SHORT).show();
                    }

                    // por seguridad, limpiamos campos de contraseña
                    etContrasenaActual.setText("");
                    etNuevaContrasena.setText("");
                    etRepetirContrasena.setText("");

                } else {
                    Toast.makeText(this, "❌ Error al guardar (" + codigo + ")", Toast.LENGTH_SHORT).show();
                    Log.w(TAG, "PUT /perfil fallo: code=" + codigo + ", body=" + cuerpo);
                }
            }));
        });

        // ===== Volver / descartar cambios =====
        btnVolver.setOnClickListener(v -> {
            rellenarUI(perfil);  // restaura lo que hay en objeto perfil
        });

        // ===== Flecha atrás del header =====
        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
        }
    }

    // ---------------- Navegación inferior ----------------
    private void setupBottomNavigation() {
        ImageView iconInicio  = findViewById(R.id.icon1);
        ImageView iconMapa    = findViewById(R.id.icon2);
        ImageView iconQR      = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil  = findViewById(R.id.icon5);

        iconInicio.setOnClickListener(v ->
                startActivity(new Intent(this, HomeActivity.class)));

        iconMapa.setOnClickListener(v ->
                startActivity(new Intent(this, MapaActivity.class)));

        iconQR.setOnClickListener(v ->
                startActivity(new Intent(this, ConnectionActivity.class)));

        iconAlertas.setOnClickListener(v ->
                startActivity(new Intent(this, IncidenciaActivity.class)));

        iconPerfil.setOnClickListener(v ->
                startActivity(new Intent(this, PerfilActivity.class)));
    }

    // ---------------- Carga de datos ----------------
    private void cargarPerfil() {
        setEnabled(false);

        perfil = new PerfilFake(this, (p, desdeServidor) -> runOnUiThread(() -> {
            setEnabled(true);
            perfil = p;
            rellenarUI(perfil);

            String targetaCargada = perfil.getTarjeta();
            if (targetaCargada != null && !targetaCargada.isEmpty()) {
                Toast.makeText(this,
                        desdeServidor ?
                                "Perfil cargado - Targeta ID: " + targetaCargada
                                : "Usando datos locales - Targeta ID: " + targetaCargada,
                        Toast.LENGTH_LONG).show();
            } else {
                Toast.makeText(this,
                        desdeServidor ? "Perfil cargado desde el servidor"
                                : "No hay token o conexión. Usando datos locales.",
                        Toast.LENGTH_SHORT).show();
            }
        }));
    }

    /** Rellena los campos visibles (nunca contraseña) */
    private void rellenarUI(PerfilFake p) {
        if (p == null) return;
        Log.d("PerfilActivity", "rellenarUI: " + p.toString());
        etNombre.setText(nv(p.getNombre()));
        etCorreo.setText(nv(p.getCorreo()));
        etTarjeta.setText(nv(p.getTarjeta()));

        // por seguridad, nunca mostramos contraseñas
        etContrasenaActual.setText("");
        etNuevaContrasena.setText("");
        etRepetirContrasena.setText("");

    }

    // ---------------- Validaciones (igual que web) ----------------
    private boolean validateInputs() {
        String nombre  = s(etNombre.getText());
        String correo  = s(etCorreo.getText());
        String tarjeta = s(etTarjeta.getText());

        String actual  = s(etContrasenaActual.getText());
        String nueva   = s(etNuevaContrasena.getText());
        String repetir = s(etRepetirContrasena.getText());

        // 1) Nombre obligatorio
        if (nombre.isEmpty()) {
            etNombre.setError("Campo requerido");
            etNombre.requestFocus();
            return false;
        }

        // 2) Correo obligatorio + validación
        if (correo.isEmpty()) {
            etCorreo.setError("Campo requerido");
            etCorreo.requestFocus();
            return false;
        }
        if (!Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            etCorreo.setError("Correo inválido");
            etCorreo.requestFocus();
            return false;
        }

        // 3) targeta_id opcional, pero max 9 chars si se rellena
        if (!tarjeta.isEmpty() && tarjeta.length() > 9) {
            etTarjeta.setError("Máximo 9 caracteres");
            etTarjeta.requestFocus();
            return false;
        }

        // 4) contraseña actual SIEMPRE obligatoria
        if (actual.isEmpty()) {
            etContrasenaActual.setError("Debes introducir tu contraseña actual");
            etContrasenaActual.requestFocus();
            return false;
        }

        // 5) nueva contraseña / repetir: solo si quiere cambiarla
        boolean quiereCambiar = !nueva.isEmpty() || !repetir.isEmpty();

        if (quiereCambiar) {
            if (nueva.isEmpty()) {
                etNuevaContrasena.setError("Introduce la nueva contraseña");
                etNuevaContrasena.requestFocus();
                return false;
            }
            if (repetir.isEmpty()) {
                etRepetirContrasena.setError("Debes repetir la nueva contraseña");
                etRepetirContrasena.requestFocus();
                return false;
            }

            if (!nueva.equals(repetir)) {
                etRepetirContrasena.setError("Las nuevas contraseñas no coinciden");
                etRepetirContrasena.requestFocus();
                return false;
            }

            if (!PASS_PATTERN.matcher(nueva).matches()) {
                etNuevaContrasena.setError(
                        "La nueva contraseña no cumple los requisitos:\n" +
                                "mínimo 8 caracteres, con mayúsculas, minúsculas, números y símbolos (@$!%*?&)"
                );
                etNuevaContrasena.requestFocus();
                return false;
            }
        }

        return true;
    }

    // ---------------- Utilidades ----------------
    private void setEnabled(boolean enabled) {
        btnGuardar.setEnabled(enabled);
        btnVolver.setEnabled(enabled);

        etNombre.setEnabled(enabled);
        etCorreo.setEnabled(enabled);
        etTarjeta.setEnabled(enabled);
        etContrasenaActual.setEnabled(enabled);
        etNuevaContrasena.setEnabled(enabled);
        etRepetirContrasena.setEnabled(enabled);
    }

    private String s(CharSequence cs) {
        return cs == null ? "" : cs.toString().trim();
    }

    private String nv(String s) {
        return s == null ? "" : s;
    }
}
