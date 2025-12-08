/**
 * Fichero: RegisterActivity.java
 * Descripción: Actividad para el registro del usuario con verificación por email.
 * @author Denys Litvynov Lymanets
 * @version 2.0
 * @since 16/11/2025
 */

package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.CheckBox;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.RegistroFake;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import com.google.android.material.textfield.TextInputLayout;
import android.util.Patterns;

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class RegisterActivity extends AppCompatActivity {

    private CheckBox aceptaPoliticaCheckBox; // ← nuevo: checkbox de política

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        TextInputLayout nameInputLayout = findViewById(R.id.nameInputLayout);
        TextInputLayout lastnameInputLayout = findViewById(R.id.lastnameInputLayout);
        TextInputLayout emailInputLayout = findViewById(R.id.emailInputLayout);
        TextInputLayout cardIdInputLayout = findViewById(R.id.cardIdInputLayout);
        TextInputLayout passwordInputLayout = findViewById(R.id.passwordInputLayout);
        TextInputLayout repeatPasswordInputLayout = findViewById(R.id.repeatPasswordInputLayout);


        // Configurar el botón de retroceso
        MaterialButton backButton = findViewById(R.id.backButton);
        backButton.setOnClickListener(v -> {
            onBackPressed();
        });

        // Campos del formulario
        TextInputEditText nameEditText = findViewById(R.id.nameEditText);
        TextInputEditText surnameEditText = findViewById(R.id.lastnameEditText);
        TextInputEditText emailEditText = findViewById(R.id.emailEditText);
        TextInputEditText cardIdEditText = findViewById(R.id.cardIdEditText);
        TextInputEditText passwordEditText = findViewById(R.id.passwordEditText);
        TextInputEditText repeatPasswordEditText = findViewById(R.id.repeatPasswordEditText);
        MaterialButton registerButton = findViewById(R.id.registerButton);
        TextView loginLink = findViewById(R.id.loginLinkTextView);


        // ← NUEVO: checkbox de política
        aceptaPoliticaCheckBox = findViewById(R.id.acepta_politica_checkbox);

        // -------------------------------------------------------------------------------
        // -------------------------------------------------------------------------------

        RegistroFake registroFake = new RegistroFake();

        registerButton.setOnClickListener(v -> {
            String nombre = nameEditText.getText() != null
                    ? nameEditText.getText().toString().trim() : "";
            String apellido = surnameEditText.getText() != null
                    ? surnameEditText.getText().toString().trim() : "";
            String correo = emailEditText.getText() != null
                    ? emailEditText.getText().toString().trim() : "";
            String targetaId = cardIdEditText.getText() != null
                    ? cardIdEditText.getText().toString().trim() : "";
            String contrasena = passwordEditText.getText() != null
                    ? passwordEditText.getText().toString().trim() : "";
            String contrasenaRepite = repeatPasswordEditText.getText() != null
                    ? repeatPasswordEditText.getText().toString().trim() : "";
            boolean aceptaPolitica = aceptaPoliticaCheckBox.isChecked();

            // Limpiar errores previos
            nameInputLayout.setError(null);
            lastnameInputLayout.setError(null);
            emailInputLayout.setError(null);
            cardIdInputLayout.setError(null);
            passwordInputLayout.setError(null);
            repeatPasswordInputLayout.setError(null);

            boolean hayError = false;

            // Nombre
            if (nombre.isEmpty()) {
                nameInputLayout.setError("Debes introducir un nombre");
                hayError = true;
            }

            // Apellidos
            if (apellido.isEmpty()) {
                lastnameInputLayout.setError("Debes introducir los apellidos");
                hayError = true;
            }

            // Correo
            if (correo.isEmpty()) {
                emailInputLayout.setError("Debes introducir un correo");
                hayError = true;
            } else if (!Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
                emailInputLayout.setError("Formato de correo no válido");
                hayError = true;
            }

            // ID tarjeta
            if (targetaId.isEmpty()) {
                cardIdInputLayout.setError("Debes introducir un ID de tarjeta");
                hayError = true;
            }

            // Contraseña
            if (contrasena.isEmpty()) {
                passwordInputLayout.setError("Debes introducir una contraseña");
                hayError = true;
            }

            // Repetir contraseña
            if (contrasenaRepite.isEmpty()) {
                repeatPasswordInputLayout.setError("Debes repetir la contraseña");
                hayError = true;
            }

            // Si ya hay errores, no seguimos
            if (hayError) return;

            // Política de privacidad
            if (!aceptaPolitica) {
                Toast.makeText(this,
                        "Debes aceptar la política de privacidad y términos",
                        Toast.LENGTH_SHORT).show();
                return;
            }

            // Coincidencia de contraseñas
            if (!contrasena.equals(contrasenaRepite)) {
                repeatPasswordInputLayout.setError("Las contraseñas no coinciden");
                return;
            }

            // -------------------------------------------------------------------------------
            // -------------------------------------------------------------------------------

            // Enviar al backend
            registroFake.registro(nombre, apellido, correo, targetaId, contrasena, contrasenaRepite, aceptaPolitica,
                    new RegistroFake.RegistroCallback() {
                        @Override
                        public void onCodigoEnviado() {
                            Log.d("RegisterActivity", "onCodigoEnviado() llamado → abriendo VerifyRegistrationActivity");
                            try {
                                Intent intent = new Intent(RegisterActivity.this, VerifyRegistrationActivity.class);
                                intent.putExtra("correo", correo);
                                startActivity(intent);
                                // Opcional: cerrar registro para no volver atrás
                                // finish();
                            } catch (Exception e) {
                                Log.e("RegisterActivity", "ERROR al abrir VerifyRegistrationActivity", e);
                                Toast.makeText(RegisterActivity.this, "Error interno: " + e.getMessage(), Toast.LENGTH_LONG).show();
                            }
                        }

                        @Override
                        public void onError(String error) {
                            Toast.makeText(RegisterActivity.this, error, Toast.LENGTH_LONG).show();
                        }
                    });
        });

        // -------------------------------------------------------------------------------
        // -------------------------------------------------------------------------------

        // Enlace para ir al login
        loginLink.setOnClickListener(v -> {
            startActivity(new Intent(this, LoginActivity.class));
        });
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------