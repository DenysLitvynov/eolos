//Recompensas JS
//@description: Scrpt con funcionalidad de las recompensas
//
//@Author: Ariel Bejaran 

import { RecompensasFake } from "../logica_fake/recompensas_fake.js"; 
const recompensasFake = new RecompensasFake();

function cargar_recompensas() {
    recompensasFake.obtenerRecompensas().then(recompensas => {
        const contenedor = document.getElementById('nextRewards');

        contenedor.innerHTML = '';  // Limpiar el contenedor antes de agregar nuevas recompensas
        recompensas.forEach(recompensa => {
            const tarjeta = document.createElement('div');
            tarjeta.className = 'tarjeta-recompensa';
            tarjeta.innerHTML = `

             <button class="reward-item" type="button">
                <span class="reward-item__logo">🍔</span>
                <span class="reward-item__text">${recompensa.descripcion}</span>
              </button>

                `;
            contenedor.appendChild(tarjeta);
        }
        );
    });

}

document.addEventListener('DOMContentLoaded', function () {
    cargar_recompensas();
});
