/**========================
 * GESTION DE INCIDENCIAS.js
 * =========================
 *  Script que maneja la funcionalidad de la pagina de gestion de incidencias.
 * @author Ariel Bejaran
 * @todo implementar la conexión con la base de datos para obtener y actualizar el estado de las incidencias.
 * ========================
 */

//clase pop up que nos permite hacer pop ups dinamicos
import { Popup } from '../utilidades/class_popup.js';



//Función para extraer los datos de la tarjeta DOM ---
/**
 * Extrae y estructura los datos de una tarjeta de incidencia.
 * @param {HTMLElement} tarjeta - El elemento DOM de la tarjeta de incidencia.
 * @returns {object} Un objeto con todos los datos de la incidencia.
 */
function obtenerDatosIncidencia(tarjeta) {
    const tituloIncidencia = tarjeta.querySelector('.titulo-incidencia').textContent;
    const tiempo = tarjeta.querySelector('.detalle-incidencia.tiempo').textContent;
    const fuente = tarjeta.querySelector('.detalle-incidencia.fuente').textContent;
    
    // Determinar el estado
    const estadoElement = tarjeta.querySelector('.encabezado-estado');
    const esResuelto = estadoElement.classList.contains('estado-resuelto');
    const estadoTexto = esResuelto ? 'RESUELTO' : 'NO RESUELTO';
    const actionText = esResuelto ? 'Reabrir Incidencia' : 'Marcar como Resuelto';

    // Datos Fijos (por ahora, se simularán con datos reales de la DB en el futuro)
    const paradaIncidencia = "Parada: Alboraya"; 
    const idUsuarioUnico = "ID Usuario: 1821981"; 

    return {
        titulo: tituloIncidencia,
        tiempo: tiempo,
        fuente: fuente,
        esResuelto: esResuelto,
        estadoTexto: estadoTexto,
        actionText: actionText,
        parada: paradaIncidencia,
        idUsuario: idUsuarioUnico
    };
}

//Función para construir el contenido HTML del pop-up ---
/**
 * Crea el contenedor principal (header, detalles, botón) del pop-up.
 * @param {object} datos - Los datos de la incidencia obtenidos de la tarjeta.
 * @returns {HTMLElement} El elemento DIV que contiene todo el cuerpo del pop-up.
 */
function crearContenidoPopup(datos) {
    const contenidoPopup = document.createElement('div');
    
    const subtitle = document.createElement('h3');
    subtitle.textContent = 'Datos de la incidencia';
    contenidoPopup.appendChild(subtitle);
    
    const detalleWrapper = document.createElement('div');
    detalleWrapper.className = 'popup-detailed-content'; 

    const ul = document.createElement('ul');
    ul.innerHTML = `
        <li><strong>${datos.tiempo}</strong></li>
        <li><strong>${datos.parada}</strong></li>
        <li><strong>${datos.idUsuario}</strong></li>
        <li><strong>Tipo:</strong> ${datos.fuente}</li> 
    `;
    
    const statusDiv = document.createElement('div');
    statusDiv.textContent = datos.estadoTexto;
    statusDiv.className = datos.esResuelto ? 'estado-pop-up resuelto' : 'estado-pop-up no-resuelto';
    
    const statusLi = document.createElement('li');
    statusLi.className = 'li-status'; 
    statusLi.appendChild(statusDiv);
    ul.appendChild(statusLi);

    detalleWrapper.appendChild(ul);
    contenidoPopup.appendChild(detalleWrapper);

    const actionButton = document.createElement('button');
    actionButton.textContent = datos.actionText;
    actionButton.className = 'popup-action-btn fas fa-check'; 

    // Función de Acción (Simulación - se necesita la instancia del popup para cerrarlo)
    const handleAction = () => {
        console.log(`Incidencia "${datos.titulo}" marcada como ${datos.esResuelto ? 'reabierta' : 'resuelta'} (Simulación)`); 
        // Nota: El popup se cerrará fuera de esta función, después de la creación.
    };
    actionButton.addEventListener('click', handleAction);
    
    contenidoPopup.appendChild(actionButton);
    
    // Devolvemos el contenedor completo y el botón para añadir el listener de cierre
    return { contenido: contenidoPopup, actionButton: actionButton };
}

// Función principal para configurar eventos ---
function configurarEventosIncidencias() {
    // Obtener todas las tarjetas de incidencia
    const tarjetas = document.querySelectorAll('.tarjeta-incidencia');

    tarjetas.forEach(tarjeta => {
        tarjeta.addEventListener('click', (event) => {
            event.stopPropagation(); 
            
            const datosIncidencia = obtenerDatosIncidencia(tarjeta);
            const { contenido, actionButton } = crearContenidoPopup(datosIncidencia);
            
            const incidenciaPopup = new Popup(
                datosIncidencia.titulo, 
                contenido 
            );
            
            // Paso D: Actualizar el listener del botón de acción para cerrar el pop-up
            actionButton.removeEventListener('click', actionButton.handleAction); // Eliminar listener temporal si existiera
            actionButton.addEventListener('click', () => {
                // Aquí ejecutamos la lógica de acción que estaba en crearContenidoPopup
                console.log(`Incidencia "${datosIncidencia.titulo}" marcada como ${datosIncidencia.esResuelto ? 'reabierta' : 'resuelta'} (Simulación)`); 
                incidenciaPopup.cerrarPopup(); // Cierra el pop-up después de la acción
            });


            incidenciaPopup.abrirPopup();
        });
    });
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', configurarEventosIncidencias);