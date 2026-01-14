//Recompensas JS
//@description: Scrpt con funcionalidad de las recompensas
//
//S@ Author: Ariel Bejaran 



import { RecompensasFake } from "../logica_fake/recompensas_fake.js";
import { Popup } from '../utilidades/class_popup.js';

const recompensasFake = new RecompensasFake();


function icon_selector(descripcion) {
    // Convertimos a minúsculas para que la búsqueda no sea sensible a mayúsculas
    const texto = descripcion.toLowerCase();

    switch (true) {
        case texto.includes('mc') || texto.includes('hamburguesa')|| texto.includes('comida'):
            return '🍔';
            
        case texto.includes('bebida') || texto.includes('copa'):
            return '🍹';
            
        case texto.includes('tecnología') || texto.includes('pc') || texto.includes('web'):
            return '💻';

        case texto.includes('cafe') || texto.includes('panaria') || texto.includes('cafetería'):
            return '☕';
        
        case texto.includes('helado') || texto.includes('heladeria'):
            return '🍦';

        case texto.includes('bici') || texto.includes('kilómetros') || texto.includes('rueda') || texto.includes('mantenimiento'):
            return '🚲';

        default:
            return '🎁'; 
    }
}


async function cargar_sistema_recompensas() {
    try {
        const data = await recompensasFake.obtenerRecompensasUsuario(); 
        
        const contenedorObtenidas = document.getElementById('availableRewards');
        const contenedorProximas = document.getElementById('nextRewards');

        contenedorObtenidas.innerHTML = '';
        contenedorProximas.innerHTML = '';

        // 1. Renderizar Obtenidas (Interactivos: abren popup)
        data.obtenidas.forEach(recompensa => {
            contenedorObtenidas.appendChild(crearTarjeta(recompensa, true));
        });

        // 2. Renderizar Próximas (No interactivos o bloqueados)
        data.proximas.forEach(recompensa => {
            contenedorProximas.appendChild(crearTarjeta(recompensa, false));
        });

    } catch (error) {
        console.error("Error al cargar recompensas:", error);
    }
}

function crearTarjeta(recompensa, esObtenida = false) {
    const tarjeta = document.createElement('div');
    tarjeta.className = 'tarjeta-recompensa';
    
    // Creamos el HTML
    tarjeta.innerHTML = `
        <button class="reward-item" type="button" ${!esObtenida ? 'style="opacity: 0.6; cursor: default;"' : ''}>
            <span class="reward-item__logo">${icon_selector(recompensa.descripcion)}</span>
            <span class="reward-item__text">${recompensa.descripcion}</span>
        </button>
    `;

    // Si la recompensa es obtenida, le asignamos el evento para abrir el popup
    if (esObtenida) {
        const boton = tarjeta.querySelector('.reward-item');
        boton.addEventListener('click', () => {
            mostrarPopupRecompensa(recompensa);
        });
    }

    return tarjeta;
}

function mostrarPopupRecompensa(recompensa) {
    const contenidoPopup = document.createElement('div');
    
    const subtitle = document.createElement('h2');
    subtitle.textContent = 'Detalles de tu recompensa';
    contenidoPopup.appendChild(subtitle);
    
    const detalleWrapper = document.createElement('div');
    detalleWrapper.className = 'popup-detailed-content'; 

    const ul = document.createElement('ul');
    ul.innerHTML = `
        <li><strong>Premio:</strong> ${recompensa.titulo}</li>
        <li><strong>Descripción:</strong> ${recompensa.descripcion}</li>
    `;

    const qrLi = document.createElement('li');
    qrLi.style.textAlign = 'center';
    qrLi.style.padding = '15px';
    qrLi.innerHTML = `
        <img src="/images/recompensa_eolos.png" 
             alt="QR" 
             style="width: 150px; background: white; padding: 10px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    `;
    ul.appendChild(qrLi);

    detalleWrapper.appendChild(ul);
    contenidoPopup.appendChild(detalleWrapper);

    const actionButton = document.createElement('button');
    actionButton.className = 'popup-action-btn fas fa-download'; 
    
    const btnText = document.createElement('span');
    btnText.textContent = ' Descargar Recompensa QR';
    btnText.style.fontFamily = 'inherit';
    btnText.style.marginLeft = '10px';
    actionButton.appendChild(btnText);

    actionButton.addEventListener('click', () => {
        const rutaImagen = `/images/recompensa_eolos.png`; 
        descargarImagen(rutaImagen, `QR_${recompensa.titulo}.png`);
    });
    
    contenidoPopup.appendChild(actionButton);

    const recompensaPopup = new Popup(recompensa.titulo, contenidoPopup);
    recompensaPopup.abrirPopup();
}

// Función auxiliar para forzar la descarga
function descargarImagen(url, nombre) {
    const link = document.createElement('a');
    link.href = url;
    link.download = nombre;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function actualizar_barra_progreso(kmActual, kmObjetivo) {
    // Validar que kmActual sea un número válido
    const actual = parseFloat(kmActual) || 0;
    const objetivo = parseFloat(kmObjetivo) || 1; // Evitar división por cero

    document.getElementById("kmText").textContent = `${actual.toFixed(1)} de ${objetivo} Km`;
    document.getElementById("kmTotal").textContent = actual.toFixed(1);

    const percent = Math.max(0, Math.min(100, (actual / objetivo) * 100));
    
    const fill = document.querySelector(".progressbar__fill");
    const bar = document.querySelector(".progressbar");

    if(fill) fill.style.width = percent + "%";
    if(bar) {
        bar.setAttribute("aria-valuenow", String(actual));
        bar.setAttribute("aria-valuemax", String(objetivo));
    }
}

async function inicializarProgreso() {
    try {
        // 1. Obtenemos los KM reales del backend
        const kmActual = await recompensasFake.obtenerDistanciaRecorrida();
        
        // 2. Definimos el objetivo (puedes traerlo de una recompensa específica o dejarlo fijo)
        const kmObjetivo = 30; 

        // 3. Actualizamos la interfaz
        actualizar_barra_progreso(kmActual, kmObjetivo);
        
    } catch (error) {
        console.error("Error inicializando progreso:", error);
        actualizar_barra_progreso(0, 30); // Estado seguro por defecto
    }
}


// Modifica tu DOMContentLoaded para llamar a la nueva función
document.addEventListener('DOMContentLoaded', function () {
    cargar_sistema_recompensas();
    inicializarProgreso(); // <--- Llamada asíncrona correcta
});
