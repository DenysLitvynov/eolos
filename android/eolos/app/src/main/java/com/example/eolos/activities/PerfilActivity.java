// com/example/eolos/activities/PerfilActivity.java
package com.example.eolos.activities;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.text.InputType;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.data.PerfilDto;
import com.example.eolos.data.PerfilRemoteDataSource;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/**
 * Clase: PerfilActivity
 * Descripción: Pantalla que permite al usuario ver, editar y guardar su información de perfil.
 *              Los datos se obtienen de una fuente remota (API) con respaldo local "fake" en caso
 *              de no tener conexión. También incluye un selector de fecha para la fecha de nacimiento.
 * Autor: JINWEI
 * Fecha: 30/09/2025
 */

public class PerfilActivity extends AppCompatActivity {

    // Campos de entrada de texto
    private EditText etNombre, etCorreo, etTarjeta, etContrasena, etFecha;
    // Botones de acción
    private Button btnGuardar, btnVolver;

    // Formato de fecha para mostrar y parsear
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("d/M/yyyy", Locale.getDefault());

    // Fuente de datos remota (maneja comunicación con servidor)
    private PerfilRemoteDataSource dataSource;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        // ------------------- Inicialización de componentes UI -------------------
        etNombre = findViewById(R.id.etNombre);
        etCorreo = findViewById(R.id.etCorreo);
        etTarjeta = findViewById(R.id.etTarjeta);
        etContrasena = findViewById(R.id.etContrasena);
        etFecha = findViewById(R.id.etFecha);
        btnGuardar = findViewById(R.id.btnGuardar);
        btnVolver = findViewById(R.id.btnVolver);

        // Inicializar el acceso remoto a los datos de perfil
        dataSource = new PerfilRemoteDataSource(this);

        // ------------------- Cargar datos del perfil -------------------
        // Se deshabilitan los botones mientras se carga la información
        setEnabled(false);

        // Se intenta obtener los datos del perfil desde el servidor.
        // Si falla, la fuente remota devuelve datos "fake" para demostración.
        dataSource.getPerfil(new PerfilRemoteDataSource.Callback<PerfilDto>() {
            @Override
            public void onSuccess(PerfilDto dto, boolean fromFake) {
                bind(dto); // Muestra los datos en los campos de texto
                setEnabled(true);
                Toast.makeText(PerfilActivity.this,
                        fromFake ? "Sin conexión: mostrando datos de demostración."
                                : "Perfil cargado desde la base de datos.",
                        Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onError(String message) {
                setEnabled(true);
                Toast.makeText(PerfilActivity.this,
                        "Error al cargar perfil: " + message,
                        Toast.LENGTH_LONG).show();
            }
        });

        // ------------------- Configuración del campo de fecha -------------------
        // Se evita que el teclado aparezca y se usa un selector de fecha.
        etFecha.setInputType(InputType.TYPE_NULL);
        etFecha.setOnClickListener(v -> showDatePicker());
        etFecha.setOnFocusChangeListener((v, hasFocus) -> { if (hasFocus) showDatePicker(); });

        // ------------------- Botón: Guardar perfil -------------------
        btnGuardar.setOnClickListener(v -> {
            // Validar los datos antes de guardar
            if (validateInputs()) {
                PerfilDto dto = collect(); // Recoge los valores del formulario
                setEnabled(false);

                // Llamada a la fuente de datos para guardar el perfil
                dataSource.savePerfil(dto, new PerfilRemoteDataSource.Callback<Boolean>() {
                    @Override
                    public void onSuccess(Boolean data, boolean fromFake) {
                        setEnabled(true);
                        Toast.makeText(PerfilActivity.this,
                                "Perfil guardado en la base de datos.",
                                Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void onError(String message) {
                        setEnabled(true);
                        Toast.makeText(PerfilActivity.this,
                                "No se pudo guardar: " + message,
                                Toast.LENGTH_LONG).show();
                    }
                });
            }
        });

        // ------------------- Botón: Volver -------------------
        btnVolver.setOnClickListener(v -> finish());
    }

    // -------------------------------------------------------------------
    // Enlaza un objeto PerfilDto con los campos de texto de la UI
    private void bind(PerfilDto d) {
        etNombre.setText(d.nombre);
        etCorreo.setText(d.correo);
        etTarjeta.setText(d.tarjeta);
        etContrasena.setText(d.contrasena);
        etFecha.setText(d.fecha);
    }

    // -------------------------------------------------------------------
    // Crea un objeto PerfilDto a partir de los valores actuales del formulario
    private PerfilDto collect() {
        return new PerfilDto(
                etNombre.getText().toString().trim(),
                etCorreo.getText().toString().trim(),
                etTarjeta.getText().toString().trim(),
                etContrasena.getText().toString(),
                etFecha.getText().toString().trim()
        );
    }

    // -------------------------------------------------------------------
    // Valida los datos introducidos por el usuario antes de guardarlos
    private boolean validateInputs() {
        String nombre = etNombre.getText().toString().trim();
        String correo = etCorreo.getText().toString().trim();
        String tarjeta = etTarjeta.getText().toString().trim();
        String pass = etContrasena.getText().toString();
        String fecha = etFecha.getText().toString().trim();

        // Validaciones básicas de campos obligatorios y formato de correo
        if (nombre.isEmpty()) { etNombre.setError("Campo requerido"); etNombre.requestFocus(); return false; }
        if (correo.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            etCorreo.setError("Correo electrónico inválido");
            etCorreo.requestFocus();
            return false;
        }
        if (tarjeta.isEmpty()) { etTarjeta.setError("Campo requerido"); etTarjeta.requestFocus(); return false; }
        if (correo.isEmpty() || !correo.contains("@")) {
            etCorreo.setError("Correo debe contener @");
            etCorreo.requestFocus();
            return false;
        }
        if (fecha.isEmpty()) { etFecha.setError("Campo requerido"); etFecha.requestFocus(); return false; }

        return true;
    }

    // -------------------------------------------------------------------
    // Muestra un cuadro de diálogo para seleccionar la fecha (DatePicker)
    private void showDatePicker() {
        final Calendar cal = Calendar.getInstance();
        try {
            String txt = etFecha.getText().toString();
            if (!txt.isEmpty()) cal.setTime(dateFormat.parse(txt));
        } catch (ParseException ignored) {}

        // Crea el DatePickerDialog y actualiza el campo de texto al seleccionar una fecha
        DatePickerDialog dlg = new DatePickerDialog(
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
        );
        dlg.show();
    }

    // -------------------------------------------------------------------
    // Habilita o deshabilita los botones mientras se realizan operaciones remotas
    private void setEnabled(boolean enabled) {
        btnGuardar.setEnabled(enabled);
        btnVolver.setEnabled(enabled);
    }
}
