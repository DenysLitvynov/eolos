/**
 * Fichero: RegisterActivity.java
 * Descripción: Actividad para el registro del usuario con auto-login.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 27/10/2025
 */

package com.example.eolos.activities;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.RegistroFake;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

public class RegisterActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        TextInputEditText nameEditText = findViewById(R.id.nameEditText);
        TextInputEditText surnameEditText = findViewById(R.id.lastnameEditText);
        TextInputEditText emailEditText = findViewById(R.id.emailEditText);
        TextInputEditText cardIdEditText = findViewById(R.id.cardIdEditText);
        TextInputEditText passwordEditText = findViewById(R.id.passwordEditText);
        TextInputEditText repeatPasswordEditText = findViewById(R.id.repeatPasswordEditText);
        MaterialButton registerButton = findViewById(R.id.registerButton);
        TextView loginLink = findViewById(R.id.loginLinkTextView);

        RegistroFake registroFake = new RegistroFake();

        registerButton.setOnClickListener(v -> {
            String nombre = nameEditText.getText().toString().trim();
            String apellido = surnameEditText.getText().toString().trim();
            String correo = emailEditText.getText().toString().trim();
            String targetaId = cardIdEditText.getText().toString().trim();
            String contrasena = passwordEditText.getText().toString().trim();
            String contrasenaRepite = repeatPasswordEditText.getText().toString().trim();

            if (nombre.isEmpty() || apellido.isEmpty() || correo.isEmpty() || targetaId.isEmpty() ||
                    contrasena.isEmpty() || contrasenaRepite.isEmpty()) {
                Toast.makeText(this, "Por favor, completa todos los campos", Toast.LENGTH_SHORT).show();
                return;
            }

            if (!contrasena.equals(contrasenaRepite)) {
                Toast.makeText(this, "Las contraseñas no coinciden", Toast.LENGTH_SHORT).show();
                return;
            }

            registroFake.registro(nombre, apellido, correo, targetaId, contrasena, contrasenaRepite,
                    new RegistroFake.RegistroCallback() {
                        @Override
                        public void onSuccess(String token) {
                            SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
                            prefs.edit().putString("token", token).apply();
                            Toast.makeText(RegisterActivity.this, "Registro e inicio de sesión exitosos", Toast.LENGTH_SHORT).show();
                            startActivity(new Intent(RegisterActivity.this, DashboardActivity.class));
                            finish();
                        }

                        @Override
                        public void onError(String error) {
                            Toast.makeText(RegisterActivity.this, error, Toast.LENGTH_LONG).show();
                        }
                    });
        });

        loginLink.setOnClickListener(v -> {
            startActivity(new Intent(this, LoginActivity.class));
        });
    }
}