//Recompensas JS
//@description: Scrpt con funcionalidad de las recompensas
//
//@Author: Ariel Bejaran 



import { RecompensasFake } from "../logica_fake/recompensas_fake.js"; 
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
        // Llamamos a la lógica que procesa y devuelve las listas separadas
        // Asumiendo que actualizaste el endpoint /recompensas_obtenidas
        const data = await recompensasFake.obtenerRecompensasUsuario(); 
        
        const contenedorObtenidas = document.getElementById('availableRewards');
        const contenedorProximas = document.getElementById('nextRewards');

        contenedorObtenidas.innerHTML = '';
        contenedorProximas.innerHTML = '';

        // 1. Renderizar Obtenidas (Las que ya filtró el backend y guardó)
        data.obtenidas.forEach(recompensa => {
            contenedorObtenidas.appendChild(crearTarjeta(recompensa));
        });

        // 2. Renderizar Próximas (Las que NO han sido filtradas/alcanzadas aún)
        data.proximas.forEach(recompensa => {
            contenedorProximas.appendChild(crearTarjeta(recompensa));
        });

        // 3. Actualizar barra de progreso con la primera recompensa próxima
        if (data.proximas.length > 0) {
            const kmActual = await recompensasFake.obtenerDistanciaRecorrida();
            const proximoObjetivo = data.proximas[0].criterio_num_km;
            actualizar_barra_progreso(kmActual, proximoObjetivo);
        }

    } catch (error) {
        console.error("Error al cargar recompensas:", error);
    }
}

// Función auxiliar para no repetir código de creación de HTML
function crearTarjeta(recompensa) {
    const tarjeta = document.createElement('div');
    tarjeta.className = 'tarjeta-recompensa';
    tarjeta.innerHTML = `
        <button class="reward-item" type="button">
            <span class="reward-item__logo">${icon_selector(recompensa.descripcion)}</span>
            <span class="reward-item__text">${recompensa.descripcion}</span>
        </button>
    `;
    return tarjeta;
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
