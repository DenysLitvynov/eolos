/**
 * Fichero: LoginActivity.java
 * Descripción: Actividad para el login del usuario.
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
import com.example.eolos.logica_fake.LoginFake;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        TextInputEditText emailEditText = findViewById(R.id.emailEditText);
        TextInputEditText passwordEditText = findViewById(R.id.passwordEditText);
        MaterialButton loginButton = findViewById(R.id.loginButton);
        TextView registerLink = findViewById(R.id.registerLinkTextView);

        LoginFake loginFake = new LoginFake();

        loginButton.setOnClickListener(v -> {
            String correo = emailEditText.getText().toString().trim();
            String contrasena = passwordEditText.getText().toString().trim();

            if (correo.isEmpty() || contrasena.isEmpty()) {
                Toast.makeText(this, "Por favor, completa todos los campos", Toast.LENGTH_SHORT).show();
                return;
            }

            loginFake.login(correo, contrasena, new LoginFake.LoginCallback() {
                @Override
                public void onSuccess(String token) {
                    SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
                    prefs.edit().putString("token", token).apply();
                    Toast.makeText(LoginActivity.this, "Login exitoso", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(LoginActivity.this, DashboardActivity.class));
                    finish();
                }

                @Override
                public void onError(String error) {
                    Toast.makeText(LoginActivity.this, error, Toast.LENGTH_LONG).show();
                }
            });
        });

        registerLink.setOnClickListener(v -> {
            startActivity(new Intent(this, RegisterActivity.class));
        });
    }
}