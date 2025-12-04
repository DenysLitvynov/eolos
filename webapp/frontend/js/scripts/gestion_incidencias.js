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


// Datos simulados para la prueba
const datosIncidenciasSimulados = [
    {
        titulo: "Error al Escanear QR",
        tiempo: "5min",
        fuente: "Web",
        esResuelto: false // NO RESUELTO (Rojo)
    },
    {
        titulo: "Dispositivo Desconectado",
        tiempo: "15min",
        fuente: "App Móvil",
        esResuelto: false // NO RESUELTO (Rojo)
    },
    {
        titulo: "Fallo de Servidor API",
        tiempo: "40min",
        fuente: "Sistema",
        esResuelto: true // RESUELTO (Verde)
    },
    {
        titulo: "Reporte de Impresora Lenta",
        tiempo: "1h 30min",
        fuente: "Web",
        esResuelto: false // NO RESUELTO (Rojo)
    },
    {
        titulo: "Actualización de Datos Fallida",
        tiempo: "2h",
        fuente: "App Móvil",
        esResuelto: true // RESUELTO (Verde)
    }
];

/*========================================================================
  FUNCIONAMIENTO TARJETAS
 ========================================================================*/
/**
 * Crea el elemento DOM completo para una tarjeta de incidencia.
 * @param {object} datos - Objeto con los datos de la incidencia.
 * @param {string} datos.titulo - El título de la incidencia.
 * @param {string} datos.tiempo - El tiempo transcurrido (e.g., "Hace: 5min").
 * @param {string} datos.fuente - La fuente de la incidencia (e.g., "Web").
 * @param {boolean} datos.esResuelto - True si la incidencia está resuelta.
 * @returns {HTMLElement} El elemento div.tarjeta-incidencia creado.
 */
function crearTarjetaIncidencia(datos) {
    // Determinar clases y textos basados en el estado
    const estadoClase = datos.esResuelto ? 'estado-resuelto' : 'estado-noresuelto';
    const estadoTexto = datos.esResuelto ? 'RESUELTO' : 'NO RESUELTO';

    // 1. Elemento principal: <div class="tarjeta-incidencia">
    const tarjeta = document.createElement('div');
    tarjeta.classList.add('tarjeta-incidencia');

    // 2. Encabezado de estado: <div class="encabezado-estado ...">
    const encabezadoEstado = document.createElement('div');
    encabezadoEstado.classList.add('encabezado-estado', estadoClase);

    // 3. Píldora de estado: <span class="pildora-estado">
    const pildoraEstado = document.createElement('span');
    pildoraEstado.classList.add('pildora-estado');
    pildoraEstado.textContent = estadoTexto;
    encabezadoEstado.appendChild(pildoraEstado);
    tarjeta.appendChild(encabezadoEstado);

    // 4. Contenido de la tarjeta: <div class="contenido-tarjeta">
    const contenidoTarjeta = document.createElement('div');
    contenidoTarjeta.classList.add('contenido-tarjeta');

    // 5. Título: <h2 class="titulo-incidencia">
    const titulo = document.createElement('h2');
    titulo.classList.add('titulo-incidencia');
    titulo.textContent = datos.titulo;
    contenidoTarjeta.appendChild(titulo);

    // 6. Detalles: Tiempo y Fuente
    const tiempo = document.createElement('p');
    tiempo.classList.add('detalle-incidencia', 'tiempo');
    // Asegurarse de que el texto de tiempo se pase con el prefijo "Hace:"
    tiempo.textContent = datos.tiempo.startsWith('Hace:') ? datos.tiempo : `Hace: ${datos.tiempo}`; 
    contenidoTarjeta.appendChild(tiempo);

    const fuente = document.createElement('p');
    fuente.classList.add('detalle-incidencia', 'fuente');
    fuente.textContent = datos.fuente;
    contenidoTarjeta.appendChild(fuente);
    
    // Añadir contenido al contenedor principal
    tarjeta.appendChild(contenidoTarjeta);

    // Devolver la tarjeta completa
    return tarjeta;
}

/**
 * Inserta múltiples tarjetas de incidencia en el contenedor 'grid-incidencias'.
 * @param {Array<object>} incidencias - Array de objetos de datos de incidencia.
 */
function insertarIncidencias(incidencias) {
    // Usamos el ID de contenedor proporcionado: 'grid-incidencias'
    const contenedor = document.getElementById('grid-incidencias'); 
    
    if (!contenedor) {
        console.error("Error: No se encontró el contenedor con ID 'grid-incidencias'.");
        return;
    }

    incidencias.forEach(incidencia => {
        const tarjeta = crearTarjetaIncidencia(incidencia);
        contenedor.appendChild(tarjeta);
    });
}


/*========================================================================
  FUNCIONAMIENTO POP-UPS
 ========================================================================*

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
    const actionText = esResuelto ? 'cerrar incidencia' : 'Marcar como Resuelto';

    // Datos Fijos (por ahora, se simularán con datos reales de la DB en el futuro)
    const idUsuarioUnico = "ID Usuario: 1821981"; 

    return {
        titulo: tituloIncidencia,
        tiempo: tiempo,
        fuente: fuente,
        esResuelto: esResuelto,
        estadoTexto: estadoTexto,
        actionText: actionText,
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
    
    const subtitle = document.createElement('h2');
    subtitle.textContent = 'Datos de la incidencia';
    contenidoPopup.appendChild(subtitle);
    
    const detalleWrapper = document.createElement('div');
    detalleWrapper.className = 'popup-detailed-content'; 

    const ul = document.createElement('ul');
    ul.innerHTML = `
        <li>${datos.tiempo}</li>
        <li>${datos.fuente}</li> 
        <li>${datos.idUsuario}</li>
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
        console.log(`Incidencia "${datos.titulo}" marcada como ${datos.esResuelto ? 'cerrada' : 'resuelta'} (Simulación)`); 
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
            
            actionButton.removeEventListener('click', actionButton.handleAction); // Eliminar listener temporal si existiera
            actionButton.addEventListener('click', () => {
                // Aquí ejecutamos la lógica de acción que estaba en crearContenidoPopup
                console.log(`Incidencia "${datosIncidencia.titulo}" marcada como ${datosIncidencia.esResuelto ? 'cerrada' : 'resuelta'} (Simulación)`); 
                incidenciaPopup.cerrarPopup(); // Cierra el pop-up después de la acción
            });


            incidenciaPopup.abrirPopup();
        });
    });
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // 1. Insertar las tarjetas en 'grid-incidencias'
    insertarIncidencias(datosIncidenciasSimulados);
    
    // 2. Configurar los eventos de clic para los popups
    configurarEventosIncidencias();
});
