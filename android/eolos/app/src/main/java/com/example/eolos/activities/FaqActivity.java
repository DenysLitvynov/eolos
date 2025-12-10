package com.example.eolos.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.LinearLayout;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;


import com.example.eolos.Adapters.FaqAdapter;
import com.example.eolos.Models.Faq_Item;
import com.example.eolos.R;

import java.util.ArrayList;
import java.util.List;

public class FaqActivity extends AppCompatActivity {

    private RecyclerView rvFaq;

    private void setupBottomNavigation() {
        LinearLayout bottomNav = findViewById(R.id.bottom_navigation);
        if (bottomNav == null) return;

        ImageView iconInicio  = bottomNav.findViewById(R.id.icon1);
        ImageView iconMapa    = bottomNav.findViewById(R.id.icon2);
        ImageView iconQR      = bottomNav.findViewById(R.id.icon3);
        ImageView iconAlertas = bottomNav.findViewById(R.id.icon4);
        ImageView iconPerfil  = bottomNav.findViewById(R.id.icon5);

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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_faq);

        ImageView backArrow = findViewById(R.id.back_arrow);
        if (backArrow != null) {
            backArrow.setOnClickListener(v ->
                    getOnBackPressedDispatcher().onBackPressed()
            );
        }

        rvFaq = findViewById(R.id.rv_faq);
        rvFaq.setLayoutManager(new LinearLayoutManager(this));

        List<Faq_Item> faqList = crearFaqsDesdeStrings();
        FaqAdapter adapter = new FaqAdapter(faqList);
        rvFaq.setAdapter(adapter);


    }

    private List<Faq_Item> crearFaqsDesdeStrings() {
        List<Faq_Item> list = new ArrayList<>();

        list.add(new Faq_Item(
                getString(R.string.faq_1_pregunta),
                getString(R.string.faq_1_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_2_pregunta),
                getString(R.string.faq_2_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_3_pregunta),
                getString(R.string.faq_3_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_4_pregunta),
                getString(R.string.faq_4_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_5_pregunta),
                getString(R.string.faq_5_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_6_pregunta),
                getString(R.string.faq_6_respuesta)
        ));

        list.add(new Faq_Item(
                getString(R.string.faq_7_pregunta),
                getString(R.string.faq_7_respuesta)
        ));

        return list;
    }
}