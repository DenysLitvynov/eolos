package com.example.eolos.activities;

import android.app.DatePickerDialog;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.eolos.R;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/**
 * PerfilActivity (Java)
 * - 显示与编辑用户资料
 * - 使用 SharedPreferences 持久化本地数据
 * - 点击“Fecha Registro”弹出日期选择器
 */
public class PerfilActivity extends AppCompatActivity {

    private SharedPreferences prefs;

    private EditText etNombre;
    private EditText etCorreo;
    private EditText etTarjeta;
    private EditText etContrasena;
    private EditText etFecha;
    private Button btnGuardar;
    private Button btnVolver;

    private final SimpleDateFormat dateFormat = new SimpleDateFormat("d/M/yyyy", Locale.getDefault());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        // 1) 绑定视图
        etNombre = findViewById(R.id.etNombre);
        etCorreo = findViewById(R.id.etCorreo);
        etTarjeta = findViewById(R.id.etTarjeta);
        etContrasena = findViewById(R.id.etContrasena);
        etFecha = findViewById(R.id.etFecha);
        btnGuardar = findViewById(R.id.btnGuardar);
        btnVolver = findViewById(R.id.btnVolver);

        // 2) 偏好存储
        prefs = getSharedPreferences("perfil_prefs", MODE_PRIVATE);

        // 3) 加载已保存数据（没有则给默认）
        loadProfile();

        // 4) 日期选择器
        etFecha.setInputType(InputType.TYPE_NULL); // 防止键盘弹出
        etFecha.setOnClickListener(v -> showDatePicker());
        etFecha.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) showDatePicker();
        });

        // 5) 保存
        btnGuardar.setOnClickListener(v -> {
            if (validateInputs()) {
                saveProfile();
                Toast.makeText(this, "Perfil guardado correctamente", Toast.LENGTH_SHORT).show();
            }
        });

        // 6) 返回
        btnVolver.setOnClickListener(v -> finish());
    }

    private void loadProfile() {
        String nombre = prefs.getString("nombre", "Juan Bautista Peris");
        String correo = prefs.getString("correo", "juanba@gmail.com");
        String tarjeta = prefs.getString("tarjeta", "12345HDC");
        String contrasena = prefs.getString("contrasena", "********");
        String fecha = prefs.getString("fecha", "1/1/2025");

        etNombre.setText(nombre);
        etCorreo.setText(correo);
        etTarjeta.setText(tarjeta);
        etContrasena.setText(contrasena);
        etFecha.setText(fecha);
    }

    private void saveProfile() {
        prefs.edit()
                .putString("nombre", etNombre.getText().toString().trim())
                .putString("correo", etCorreo.getText().toString().trim())
                .putString("tarjeta", etTarjeta.getText().toString().trim())
                .putString("contrasena", etContrasena.getText().toString())
                .putString("fecha", etFecha.getText().toString().trim())
                .apply();
    }

    private boolean validateInputs() {
        String nombre = etNombre.getText().toString().trim();
        String correo = etCorreo.getText().toString().trim();
        String tarjeta = etTarjeta.getText().toString().trim();
        String pass = etContrasena.getText().toString();
        String fecha = etFecha.getText().toString().trim();

        if (nombre.isEmpty()) {
            etNombre.setError("Requerido");
            etNombre.requestFocus();
            return false;
        }
        if (correo.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(correo).matches()) {
            etCorreo.setError("Correo inválido");
            etCorreo.requestFocus();
            return false;
        }
        if (tarjeta.isEmpty()) {
            etTarjeta.setError("Requerido");
            etTarjeta.requestFocus();
            return false;
        }
        if (pass.isEmpty()) {
            etContrasena.setError("Requerido");
            etContrasena.requestFocus();
            return false;
        }
        if (fecha.isEmpty()) {
            etFecha.setError("Requerido");
            etFecha.requestFocus();
            return false;
        }
        return true;
    }

    private void showDatePicker() {
        final Calendar cal = Calendar.getInstance();

        // 如果已经有日期，尝试解析后作为初始日期
        try {
            String txt = etFecha.getText().toString();
            if (!txt.isEmpty()) {
                cal.setTime(dateFormat.parse(txt));
            }
        } catch (ParseException ignored) {}

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
}
