package com.example.eolos.activities;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import com.example.eolos.logica_fake.IncidenciaFake;

public class IncidenciaActivity extends AppCompatActivity {

    private static final String TAG = "IncidenciaActivity";

    private EditText etBikeCode;
    private EditText etOther;
    private RadioGroup rgBikeEnv;
    private RadioGroup rgCommApp;
    private Button btnSend;
    private Button btnCancel;

    private boolean isInternalChange = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // ⚠️ Aquí debes usar el nombre real del layout
        setContentView(R.layout.activity_incidecia);

        initViews();
        setupRadioGroups();
        updateOtherFieldState();
        setupButtons();
        setupBottomNavigation();

        // FLECHA ATRÁS DEL HEADER
        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
            // o simplemente: finish();
        }

    }

    private void setupBottomNavigation() {

        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

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

    private void initViews() {
        etBikeCode = findViewById(R.id.et_bike_code);
        etOther    = findViewById(R.id.et_other);
        rgBikeEnv  = findViewById(R.id.rg_bike_env);
        rgCommApp  = findViewById(R.id.rg_comm_app);
        btnSend    = findViewById(R.id.btn_send);
        btnCancel  = findViewById(R.id.btn_cancel);

        // Por defecto, el campo “Otro tipo” no es editable
        etOther.setEnabled(false);
        etOther.setHint("Selecciona \"Otro\" para escribir");
    }


    private void setupRadioGroups() {
        rgBikeEnv.setOnCheckedChangeListener((group, checkedId) -> {
            if (isInternalChange) return;

            // Si se selecciona una opción en el primer grupo,
            // se desmarca automáticamente el segundo grupo
            if (checkedId != -1) {
                isInternalChange = true;
                rgCommApp.clearCheck();
                isInternalChange = false;
            }
            updateOtherFieldState();
        });

        rgCommApp.setOnCheckedChangeListener((group, checkedId) -> {
            if (isInternalChange) return;

            // Si se selecciona una opción en el segundo grupo,
            // se desmarca automáticamente el primero
            if (checkedId != -1) {
                isInternalChange = true;
                rgBikeEnv.clearCheck();
                isInternalChange = false;
            }
            updateOtherFieldState();
        });
    }

    /** Activa o desactiva el campo “Otro” dependiendo de si se ha seleccionado esa opción */
    private void updateOtherFieldState() {
        boolean otroSelected = false;

        int bikeCheckedId = rgBikeEnv.getCheckedRadioButtonId();
        if (bikeCheckedId != -1) {
            RadioButton rb = findViewById(bikeCheckedId);
            if ("Otro".contentEquals(rb.getText())) {
                otroSelected = true;
            }
        }

        int appCheckedId = rgCommApp.getCheckedRadioButtonId();
        if (appCheckedId != -1) {
            RadioButton rb = findViewById(appCheckedId);
            if ("Otro".contentEquals(rb.getText())) {
                otroSelected = true;
            }
        }

        // Habilitar o deshabilitar el campo
        etOther.setEnabled(otroSelected);

        if (!otroSelected) {
            etOther.setText("");
            etOther.setHint("Selecciona \"Otro\" para escribir");
        } else {
            etOther.setHint("Describe la incidencia");
        }
    }

    private void setupButtons() {
        btnSend.setOnClickListener(v -> onSendClicked());

        btnCancel.setOnClickListener(v -> {
            clearForm();
            updateOtherFieldState();
        });
    }

    /** Limpia todos los campos del formulario */
    private void clearForm() {
        etBikeCode.setText("");
        etOther.setText("");
        rgBikeEnv.clearCheck();
        rgCommApp.clearCheck();
    }

    private void onSendClicked() {
        String bikeCode = etBikeCode.getText().toString().trim(); // VLC001 / VLC045

        // Validar que se haya escrito un código de bicicleta
        if (bikeCode.isEmpty()) {
            Toast.makeText(this, "Introduce el código de la bicicleta", Toast.LENGTH_SHORT).show();
            return;
        }

        int bikeCheckedId = rgBikeEnv.getCheckedRadioButtonId();
        int appCheckedId  = rgCommApp.getCheckedRadioButtonId();

        // Validar que se haya seleccionado algún tipo de incidencia
        if (bikeCheckedId == -1 && appCheckedId == -1) {
            Toast.makeText(this, "Selecciona un tipo de incidencia", Toast.LENGTH_SHORT).show();
            return;
        }

        String incidentType;
        String fuente;  // admin / app

        // Si la selección es del primer grupo → fuente = admin
        if (bikeCheckedId != -1) {
            RadioButton rb = findViewById(bikeCheckedId);
            incidentType = rb.getText().toString();
            fuente = "admin";
        } else {
            // Si la selección es del segundo grupo → fuente = app
            RadioButton rb = findViewById(appCheckedId);
            incidentType = rb.getText().toString();
            fuente = "app";
        }

        String otherTxt = etOther.getText().toString().trim();
        String descripcion;

        if ("Otro".equals(incidentType)) {
            // Si se selecciona “Otro”, es obligatorio escribir una descripción
            if (otherTxt.isEmpty()) {
                Toast.makeText(this,
                        "Describe la incidencia en el campo \"Otro tipo\"",
                        Toast.LENGTH_SHORT).show();
                return;
            }
            descripcion = otherTxt;   // Se usa únicamente el texto introducido por el usuario
        } else {
            // Para opciones normales, ignorar el campo “Otro”
            descripcion = incidentType;
        }

        Log.d(TAG, "descripcion=" + descripcion + ", fuente=" + fuente);

        IncidenciaFake logica = new IncidenciaFake(this);
        logica.crearIncidencia(bikeCode, descripcion, fuente, (exito, codigo, cuerpo) -> {
            if (exito) {
                Toast.makeText(IncidenciaActivity.this,
                        "Incidencia enviada correctamente",
                        Toast.LENGTH_SHORT).show();
                clearForm();
                updateOtherFieldState();
            } else {
                Toast.makeText(IncidenciaActivity.this,
                        "Error al enviar la incidencia (" + codigo + ")",
                        Toast.LENGTH_SHORT).show();
                Log.e(TAG, "Error body=" + cuerpo);
            }
        });
    }
}
