package com.example.eolos.Adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.eolos.Models.Faq_Item;
import com.example.eolos.R;

import java.util.List;

public class FaqAdapter extends RecyclerView.Adapter<FaqAdapter.FaqViewHolder> {

    private final List<Faq_Item> faqList;

    public FaqAdapter(List<Faq_Item> faqList) {
        this.faqList = faqList;
    }

    @NonNull
    @Override
    public FaqViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_faq, parent, false);
        return new FaqViewHolder(view);
    }


    @Override
    public void onBindViewHolder(@NonNull FaqViewHolder holder, int position) {
        Faq_Item item = faqList.get(position);

        holder.tvPregunta.setText(item.getPregunta());
        holder.tvRespuesta.setText(item.getRespuesta());

        // Mostrar / ocultar respuesta según estado
        boolean expandido = item.isExpandido();
        holder.tvRespuesta.setVisibility(expandido ? View.VISIBLE : View.GONE);
        holder.ivArrow.setRotation(expandido ? 180f : 0f);

        View.OnClickListener toggleListener = v -> {
            boolean nuevoEstado = !item.isExpandido();
            item.setExpandido(nuevoEstado);
            notifyItemChanged(holder.getAdapterPosition());
        };

        holder.btnToggle.setOnClickListener(toggleListener);
        holder.itemView.setOnClickListener(toggleListener);
    }

    @Override
    public int getItemCount() {
        return faqList.size();
    }

    static class FaqViewHolder extends RecyclerView.ViewHolder {
        TextView tvPregunta;
        TextView tvRespuesta;
        FrameLayout btnToggle;
        ImageView ivArrow;

        public FaqViewHolder(@NonNull View itemView) {
            super(itemView);
            tvPregunta = itemView.findViewById(R.id.tv_pregunta);
            tvRespuesta = itemView.findViewById(R.id.tv_respuesta);
            btnToggle = itemView.findViewById(R.id.btn_toggle);
            ivArrow = itemView.findViewById(R.id.iv_arrow);
        }
    }
}
