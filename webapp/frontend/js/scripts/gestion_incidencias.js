// --- Gestión de Incidencias: Pop-up Dinámico ---
import { Popup } from '../utilidades/class_popup.js';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener todas las tarjetas de incidencia
    const tarjetas = document.querySelectorAll('.tarjeta-incidencia');

    tarjetas.forEach(tarjeta => {
        tarjeta.addEventListener('click', (event) => {
            // Evitar que el clic en los elementos internos active doble evento
            event.stopPropagation(); 
            
            // --- 2. Recolección de Datos de la Tarjeta ---
            const tituloIncidencia = tarjeta.querySelector('.titulo-incidencia').textContent;
            const tiempo = tarjeta.querySelector('.detalle-incidencia.tiempo').textContent;
            const fuente = tarjeta.querySelector('.detalle-incidencia.fuente').textContent;
            
            // Determinar el estado
            const estadoElement = tarjeta.querySelector('.encabezado-estado');
            const esResuelto = estadoElement.classList.contains('estado-resuelto');
            const estadoTexto = esResuelto ? 'RESUELTO' : 'NO RESUELTO';
            const actionText = esResuelto ? 'Reabrir Incidencia' : 'Marcar como Resuelto';


            // --- 3. Datos únicos del Pop-up (ID y Parada) ---
            const paradaIncidencia = "Parada: Alboraya"; 
            const idUsuarioUnico = "ID Usuario: 1821981"; 


            // --- 4. Contenedor principal del contenido (Lo que va debajo del header del pop-up) ---
            const contenidoPopup = document.createElement('div');
            
            // 4a. Título de la sección "Datos de la incidencia"
            const subtitle = document.createElement('h3');
            subtitle.textContent = 'Datos de la incidencia';
            contenidoPopup.appendChild(subtitle);
            
            // 4b. DETALLE WRAPPER (EL RECUADRO GRIS): Contiene la lista y el estado
            const detalleWrapper = document.createElement('div');
            detalleWrapper.className = 'popup-detailed-content'; // Corregido el nombre de la clase para coincidir con CSS

            // Detalles estructurados
            const ul = document.createElement('ul');
            // La lista incluye: Tiempo (de la tarjeta), Parada (único), ID (único), y el Tipo de Incidencia (de la tarjeta)
            ul.innerHTML = `
                <li><strong>${tiempo}</strong></li>
                <li><strong>${paradaIncidencia}</strong></li>
                <li><strong>${idUsuarioUnico}</strong></li>
            `;
            // Nota: Aquí he omitido el Tipo de Incidencia para que se parezca más a la imagen de referencia.
            
            // Estado Final (NO RESUELTO/RESUELTO)
            const statusDiv = document.createElement('div');
            statusDiv.textContent = estadoTexto;
            statusDiv.className = esResuelto ? 'estado-pop-up resuelto' : 'estado-pop-up no-resuelto';
            
            // Envolver el statusDiv en un <li> y añadirlo a la lista (solicitud del usuario)
            const statusLi = document.createElement('li');
            statusLi.className = 'li-status'; // Clase para control CSS
            statusLi.appendChild(statusDiv);
            ul.appendChild(statusLi);

            detalleWrapper.appendChild(ul);
            // Se elimina la línea original para statusDiv, ya que ahora está dentro de ul
            
            // Añadimos el recuadro gris al contenedor principal del pop-up
            contenidoPopup.appendChild(detalleWrapper);

            // 4c. Botón de Acción Principal (Marcar como Resuelto)
            const actionButton = document.createElement('button');
            actionButton.textContent = actionText;
            actionButton.className = 'popup-action-btn fas fa-check'; // Añadimos icono de FontAwesome
            
            // Función de Acción (Simulación)
            const handleAction = () => {
                console.log(`Incidencia "${tituloIncidencia}" marcada como ${esResuelto ? 'reabierta' : 'resuelta'} (Simulación)`); 
                incidenciaPopup.cerrarPopup();
            };
            actionButton.addEventListener('click', handleAction);
            
            // Añadimos el botón al contenedor principal del pop-up
            contenidoPopup.appendChild(actionButton);


            // --- 5. Crear y Abrir el Pop-up ---
            const incidenciaPopup = new Popup(
                tituloIncidencia, 
                contenidoPopup // Le pasamos el contenedor completo (Título, Recuadro Gris, Botón)
            );
            
            incidenciaPopup.abrirPopup();
        });
    });
});