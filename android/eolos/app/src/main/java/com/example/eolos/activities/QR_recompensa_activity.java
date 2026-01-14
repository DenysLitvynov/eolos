package com.example.eolos.activities;

import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.eolos.R;
import com.google.android.material.button.MaterialButton;
import java.io.OutputStream;

/**
 * @QR_recompensa_activity
 * @Autor: Ariel Bejaran
 * @Desc: Actividad android que carga y permite descargar el qr de la recompensa
 * @Fecha: 14/01/2026
 */
public class QR_recompensa_activity extends AppCompatActivity {

    private ImageView ivCodigoQr;
    private MaterialButton btnDescargar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qr_recompensa);

        // Flecha atrás (Header reutilizable)
        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v -> finish());
        }

        ivCodigoQr = findViewById(R.id.iv_codigo_qr);
        btnDescargar = findViewById(R.id.button_descargar);

        btnDescargar.setOnClickListener(v -> {
            Bitmap qrBitmap = vistaToBitmap(ivCodigoQr);
            guardarImagenEnGaleria(qrBitmap);
        });

        // Referencia al TextView del Layout
        TextView tvNombre = findViewById(R.id.tv_nombre_recompensa);

        // Recuperar el dato enviado por el Adapter
        String tituloRecibido = getIntent().getStringExtra("titulo");
        if (tituloRecibido != null) {
            tvNombre.setText(tituloRecibido);
        }

        setupBottomNavigation();
    }

    /**
     * Convierte una View (en este caso el ImageView) en un Bitmap
     */
    private Bitmap vistaToBitmap(View view) {
        Bitmap bitmap = Bitmap.createBitmap(view.getWidth(), view.getHeight(), Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        view.draw(canvas);
        return bitmap;
    }

    /**
     * Guarda el bitmap en la carpeta de Imágenes del móvil
     */
    private void guardarImagenEnGaleria(Bitmap bitmap) {
        String fileName = "EOLOS_QR_" + System.currentTimeMillis() + ".jpg";
        OutputStream fos;

        try {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Images.Media.DISPLAY_NAME, fileName);
            values.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");

            // Android 10 (API 29) o superior usa Scoped Storage
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                values.put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Eolos_Recompensas");
            }

            Uri uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
            if (uri != null) {
                fos = getContentResolver().openOutputStream(uri);
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
                if (fos != null) fos.close();
                Toast.makeText(this, "QR Guardado en la Galería", Toast.LENGTH_LONG).show();
            }
        } catch (Exception e) {
            Toast.makeText(this, "Error al guardar: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void setupBottomNavigation() {
        ImageView iconInicio = findViewById(R.id.icon1);
        ImageView iconMapa = findViewById(R.id.icon2);
        ImageView iconQR = findViewById(R.id.icon3);
        ImageView iconAlertas = findViewById(R.id.icon4);
        ImageView iconPerfil = findViewById(R.id.icon5);

        if (iconInicio != null) {
            iconInicio.setOnClickListener(v ->
                    startActivity(new Intent(this, HomeActivity.class)));
        }

        if (iconMapa != null) {
            iconMapa.setOnClickListener(v ->
                    startActivity(new Intent(this, MapaActivity.class)));
        }

        if (iconQR != null) {
            iconQR.setOnClickListener(v ->
                    startActivity(new Intent(this, ConnectionActivity.class)));
        }

        if (iconAlertas != null) {
            iconAlertas.setOnClickListener(v ->
                    startActivity(new Intent(this, IncidenciaActivity.class)));
        }

        if (iconPerfil != null) {
            iconPerfil.setOnClickListener(v ->
                    startActivity(new Intent(this, PerfilActivity.class)));
        }
    }
}