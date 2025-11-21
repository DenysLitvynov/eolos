/**
 * Fichero: VerifyRegistrationActivity.java
 * Descripción: Actividad para verificar el correo del usuario.
 * @author Denys Litvynov Lymanets
 * @version 1.0
 * @since 16/11/2025
 */

package com.example.eolos.activities;

import static androidx.core.content.ContextCompat.startActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;
import com.example.eolos.logica_fake.VerifyFake;
import com.google.android.material.textfield.TextInputEditText;

public class VerifyRegistrationActivity extends AppCompatActivity {

    private VerifyFake verifyFake;
    private TextView emailTextView;
    private TextInputEditText codeEditText;
    private Button verifyButton;
    private Button resendButton;
    private CountDownTimer countDownTimer;
    private String correo;

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_verify_registration);

        correo = getIntent().getStringExtra("correo");

        emailTextView = findViewById(R.id.emailTextView);
        codeEditText = findViewById(R.id.codeEditText);
        verifyButton = findViewById(R.id.verifyButton);
        resendButton = findViewById(R.id.resendButton);

        emailTextView.setText(correo);

        verifyFake = new VerifyFake();

        // Temporizador de 60 segundos
        startTimer();

        verifyButton.setOnClickListener(v -> verificar());

        resendButton.setOnClickListener(v -> reenviar());

        // Botón atrás
        findViewById(R.id.backButton).setOnClickListener(v -> finish());
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    private void startTimer() {
        resendButton.setEnabled(false);
        resendButton.setText("Reenviar código (60s)");
        countDownTimer = new CountDownTimer(60000, 1000) {
            public void onTick(long millisUntilFinished) {
                resendButton.setText("Reenviar código (" + (millisUntilFinished / 1000) + "s)");
            }
            public void onFinish() {
                resendButton.setEnabled(true);
                resendButton.setText("Reenviar código");
            }
        }.start();
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    private void verificar() {
        String code = codeEditText.getText().toString().trim();
        if (code.length() != 6) {
            Toast.makeText(this, "El código debe tener 6 dígitos", Toast.LENGTH_SHORT).show();
            return;
        }

        verifyFake.verificar(correo, code, new VerifyFake.VerifyCallback() {
            @Override
            public void onSuccess(String token) {
                SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
                prefs.edit().putString("token", token).apply();
                Toast.makeText(VerifyRegistrationActivity.this, "¡Registro completado!", Toast.LENGTH_SHORT).show();
                startActivity(new Intent(VerifyRegistrationActivity.this, DashboardActivity.class));
                finishAffinity(); // cierra registro + verify
            }

            @Override
            public void onError(String error) {
                Toast.makeText(VerifyRegistrationActivity.this, error, Toast.LENGTH_LONG).show();
            }
        });
    }

    // -------------------------------------------------------------------------------
    // -------------------------------------------------------------------------------

    private void reenviar() {
        verifyFake.reenviar(correo, new VerifyFake.ReenvioCallback() {
            @Override
            public void onReenviado() {
                Toast.makeText(VerifyRegistrationActivity.this, "Código reenviado", Toast.LENGTH_SHORT).show();
                startTimer();
            }

            @Override
            public void onError(String error) {
                Toast.makeText(VerifyRegistrationActivity.this, error, Toast.LENGTH_SHORT).show();
            }
        });
        startTimer();
    }
}

// -------------------------------------------------------------------------------
// -------------------------------------------------------------------------------