// --- Gestión de Incidencias: Pop-up Dinámico ---
import { Popup } from '../utilidades/class_popup.js';


document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener todas las tarjetas de incidencia
    const tarjetas = document.querySelectorAll('.tarjeta-incidencia');

    tarjetas.forEach(tarjeta => {
        tarjeta.addEventListener('click', (event) => {
            // Evitar que el clic en los elementos internos active doble evento
            event.stopPropagation(); 
            
            // --- 2. Preparar los datos para el pop-up ---
            // Clonamos el contenido para que el original se quede en su sitio
            const contenidoOriginal = tarjeta.querySelector('.contenido-tarjeta');
            const contenidoPopup = contenidoOriginal.cloneNode(true);
            
            // Obtenemos el título de la tarjeta para usarlo como título del pop-up
            const tituloIncidencia = tarjeta.querySelector('.titulo-incidencia').textContent;
            
            // Opcional: Crear un detalle extra que no esté en la tarjeta original
            const detalleExtra = document.createElement('p');
            detalleExtra.innerHTML = '<strong>Detalles Adicionales:</strong> Se ha registrado un error de conexión.';
            contenidoPopup.appendChild(detalleExtra);


            // --- 3. Crear y Abrir el Pop-up ---
            // Creamos una nueva instancia de la clase Popup.
            // Nota: Esta implementación crea un nuevo elemento HTML CADA VEZ que se abre, 
            // asegurando que siempre tengas el contenido más actualizado.
            const incidenciaPopup = new Popup(tituloIncidencia, contenidoPopup);
            
            incidenciaPopup.abrirPopup();
        });
    });
});