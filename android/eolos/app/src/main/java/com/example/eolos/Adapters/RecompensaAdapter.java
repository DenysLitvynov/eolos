package com.example.eolos.Adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.Models.Recompensa_Item;
import com.example.eolos.R;

import java.util.List;

public class RecompensaAdapter extends RecyclerView.Adapter<RecompensaAdapter.RecompensaViewHolder> {

    private final List<Recompensa_Item> recompensas;

    public RecompensaAdapter(List<Recompensa_Item> recompensas) {
        this.recompensas = recompensas;
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