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

import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.content.ContextCompat;

import android.net.Uri;
import android.widget.ImageView;

import androidx.annotation.NonNull;
import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.core.content.ContextCompat;

import java.util.concurrent.Executor;


// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------

public class LoginActivity extends AppCompatActivity {

    private BiometricPrompt biometricPrompt;
    private BiometricPrompt.PromptInfo promptInfo;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // Configurar el botón de retroceso
        MaterialButton backButton = findViewById(R.id.backButton);
        backButton.setOnClickListener(v -> {
            onBackPressed();
        });

        TextInputEditText emailEditText = findViewById(R.id.emailEditText);
        TextInputEditText passwordEditText = findViewById(R.id.passwordEditText);
        MaterialButton loginButton = findViewById(R.id.loginButton);
        TextView registerLink = findViewById(R.id.registerLinkTextView);
        TextView forgotPassword = findViewById(R.id.forgotPasswordTextView);
        ImageView biometricLoginIcon = findViewById(R.id.biometricLoginIcon);
        setupBiometricLogin(biometricLoginIcon);
        // -------------------------------------------------------------------------------
        // -------------------------------------------------------------------------------

        LoginFake loginFake = new LoginFake();

        /**
         * Acción del botón de login: valida campos y llama al backend.
         */
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
                    prefs.edit().
                            putString("token", token)
                            .putString("biometric_email", correo)
                            .apply();
                    Toast.makeText(LoginActivity.this, "Login exitoso", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                    finish();
                }

                @Override
                public void onError(String error) {
                    Toast.makeText(LoginActivity.this, error, Toast.LENGTH_LONG).show();
                }

            });

        });

        // -------------------------------------------------------------------------------
        // -------------------------------------------------------------------------------

        /**
         * Enlace para ir a la pantalla de registro.
         */
        registerLink.setOnClickListener(v -> {
            startActivity(new Intent(this, RegisterActivity.class));
        });

        /**
         * Abre la página web de recuperación de contraseña en Chrome Custom Tab.
         */
        forgotPassword.setOnClickListener(v -> {
            String url = "http://172.20.10.12:8000/pages/forgot-password.html";
            Uri uri = Uri.parse(url);
            CustomTabsIntent.Builder builder = new CustomTabsIntent.Builder();
            builder.setToolbarColor(ContextCompat.getColor(this, R.color.azul_profundo));
            builder.addDefaultShareMenuItem();
            CustomTabsIntent customTabsIntent = builder.build();
            customTabsIntent.launchUrl(this, uri);
        });
    }

    private void setupBiometricLogin(ImageView biometricLoginIcon) {
        if (biometricLoginIcon == null) return;

        BiometricManager biometricManager = BiometricManager.from(this);
        int canAuth = biometricManager.canAuthenticate(
                BiometricManager.Authenticators.BIOMETRIC_STRONG
        );

        // Si el dispositivo no soporta biometría o no hay huellas, lo deshabilitamos
        if (canAuth != BiometricManager.BIOMETRIC_SUCCESS) {
            biometricLoginIcon.setAlpha(0.3f);
            biometricLoginIcon.setClickable(false);
            biometricLoginIcon.setFocusable(false);
            return;
        }

        Executor executor = ContextCompat.getMainExecutor(this);

        biometricPrompt = new BiometricPrompt(this, executor,
                new BiometricPrompt.AuthenticationCallback() {

                    @Override
                    public void onAuthenticationSucceeded(
                            @NonNull BiometricPrompt.AuthenticationResult result) {
                        super.onAuthenticationSucceeded(result);

                        SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);

                        // 1. Recuperamos los datos del "dueño biométrico"
                        String ownerToken = prefs.getString("biometric_owner_token", null);
                        String ownerEmail = prefs.getString("biometric_owner_email", null);

                        // 2. Si no hay dueño biométrico configurado, no podemos entrar con huella
                        if (ownerToken == null || ownerToken.trim().isEmpty()) {
                            Toast.makeText(LoginActivity.this,
                                    "No hay sesión asociada a esta huella. Inicia sesión con usuario y contraseña.",
                                    Toast.LENGTH_LONG).show();
                            return;
                        }

                        // 3. Forzamos que la sesión actual sea la del dueño biométrico
                        SharedPreferences.Editor editor = prefs.edit();
                        editor.putString("token", ownerToken); // token de la primera cuenta que activó huella
                        if (ownerEmail != null) {
                            editor.putString("biometric_email", ownerEmail);
                        }
                        editor.apply();

                        // 4. Entramos en la app como ese usuario
                        Toast.makeText(LoginActivity.this,
                                "Autenticación biométrica correcta",
                                Toast.LENGTH_SHORT).show();

                        startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                        finish();
                    }

                    @Override
                    public void onAuthenticationError(int errorCode,
                                                      @NonNull CharSequence errString) {
                        super.onAuthenticationError(errorCode, errString);
                        Toast.makeText(LoginActivity.this,
                                "Error biométrico: " + errString,
                                Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void onAuthenticationFailed() {
                        super.onAuthenticationFailed();
                        Toast.makeText(LoginActivity.this,
                                "Huella no reconocida",
                                Toast.LENGTH_SHORT).show();
                    }
                });

        promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle(getString(R.string.biometric_prompt_title))
                .setSubtitle(getString(R.string.biometric_prompt_subtitle))
                .setNegativeButtonText(getString(R.string.biometric_prompt_negative))
                .build();

        biometricLoginIcon.setOnClickListener(v -> {
            SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
            boolean biometricEnabled = prefs.getBoolean("biometric_enabled", false);

            if (!biometricEnabled) {
                Toast.makeText(LoginActivity.this,
                        getString(R.string.biometric_not_enabled),
                        Toast.LENGTH_LONG).show();
                return;
            }

            biometricPrompt.authenticate(promptInfo);
        });
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------