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

function cargar_recompensas_usuario() {
    recompensasFake.obtenerRecompensasUsuario().then(recompensas => {
        const contenedor = document.getElementById('availableRewards');

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

function actualizar_barra_progreso(kmActual, kmObjetivo) {
    // Cambia estos valores cuando tengas datos reales

    document.getElementById("kmText").textContent = `${kmActual} de ${kmObjetivo} Km`;
    document.getElementById("kmTotal").textContent = kmActual;

    const percent = Math.max(0, Math.min(100, (kmActual / kmObjetivo) * 100));
    document.querySelector(".progressbar__fill").style.width = percent + "%";
    document.querySelector(".progressbar").setAttribute("aria-valuenow", String(kmActual));
    document.querySelector(".progressbar").setAttribute("aria-valuemax", String(kmObjetivo));
}


document.addEventListener('DOMContentLoaded', function () {
    cargar_recompensas();
    cargar_recompensas_usuario();
    actualizar_barra_progreso(30, 100); 
});
