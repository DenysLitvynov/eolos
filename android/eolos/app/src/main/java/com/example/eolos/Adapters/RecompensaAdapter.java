package com.example.eolos.Adapters;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.R;
import com.example.eolos.activities.QR_recompensa_activity; // Nombre sugerido para tu actividad del QR
import com.example.eolos.activities.QR_recompensa_activity;

import java.util.List;

public class RecompensaAdapter extends RecyclerView.Adapter<RecompensaAdapter.RecompensaViewHolder> {

    private final List<Recompensa_Item> recompensas;
    private final boolean esDisponible; // Para saber si habilitamos el clic y el estilo

    // Modificamos el constructor para recibir si son disponibles o no
    public RecompensaAdapter(List<Recompensa_Item> recompensas, boolean esDisponible) {
        this.recompensas = recompensas;
        this.esDisponible = esDisponible;

    }

    @NonNull
    @Override
    public RecompensaViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_recompensa, parent, false);
        return new RecompensaViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull RecompensaViewHolder holder, int position) {
        Recompensa_Item item = recompensas.get(position);

        holder.tvTitulo.setText(item.getTitulo());
        holder.ivLogo.setImageResource(item.getLogoResId());

        // 1. ESTILO VISUAL: Si no está disponible, le damos transparencia (efecto "muted" de la web)
        if (!esDisponible) {
            holder.itemView.setAlpha(0.5f); // Se ve más clarito
        } else {
            holder.itemView.setAlpha(1.0f);
        }

        // 2. LÓGICA DE CLIC:
        holder.itemView.setOnClickListener(v -> {
            if (esDisponible) {
                // Ir a la actividad del QR pasando los datos
                Intent intent = new Intent(v.getContext(), QR_recompensa_activity.class);
                intent.putExtra("titulo", item.getTitulo());
                intent.putExtra("descripcion", item.getDescripcion());
                intent.putExtra("logo", item.getLogoResId());
                v.getContext().startActivity(intent);
            } else {
                // Mensaje de que aún no la tiene
                Toast.makeText(v.getContext(), "Sigue acumulando Km para desbloquear este premio", Toast.LENGTH_SHORT).show();
            }
        });
    }


    @Override
    public int getItemCount() {
        return recompensas != null ? recompensas.size() : 0;
    }

    static class RecompensaViewHolder extends RecyclerView.ViewHolder {
        ImageView ivLogo;
        TextView tvTitulo;

        public RecompensaViewHolder(@NonNull View itemView) {
            super(itemView);
            ivLogo = itemView.findViewById(R.id.iv_logo_recompensa);
            tvTitulo = itemView.findViewById(R.id.tv_titulo_recompensa);
        }
    }
}