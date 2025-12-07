/**========================
 * GESTION DE INCIDENCIAS.js
 * =========================
 * Script que maneja la funcionalidad de la pagina de gestion de incidencias.
 * @author Ariel Bejaran
 * @todo implementar la conexión con la base de datos para obtener y actualizar el estado de las incidencias.
 * ========================
 */

//clase pop up que nos permite hacer pop ups dinamicos
import { Popup } from '../utilidades/class_popup.js';
import { GestionIncidenciasFake } from '../logica_fake/gestion_incidencias_fake.js'; // ⬅️ Usaremos esta clase

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
class IncidenciaCard {
    constructor({ titulo, tiempo, fuente, esResuelto = false }) {
        this.titulo = titulo || 'Incidencia';
        this.tiempo = tiempo || 'Hace: ahora';
        this.fuente = fuente || '';
        this.esResuelto = !!esResuelto;
    }

    render() {
        const card = document.createElement('div');
        card.classList.add('tarjeta-incidencia');

        const estadoClase = this.esResuelto ? 'estado-resuelto' : 'estado-noresuelto';
        const estadoTexto = this.esResuelto ? 'RESUELTO' : 'NO RESUELTO';

        card.innerHTML = `
            <div class="encabezado-estado ${estadoClase}">
                <span class="pildora-estado">${estadoTexto}</span>
            </div>
            <div class="contenido-tarjeta">
                <h2 class="titulo-incidencia">${this.titulo}</h2>
                <p class="detalle-incidencia tiempo">${this.tiempo.startsWith('Hace:') ? this.tiempo : 'Hace: ' + this.tiempo}</p>
                <p class="detalle-incidencia fuente">${this.fuente}</p>
            </div>
        `;

        return card;
    }
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

    // Defensive: aceptar objeto único o null
    if (!incidencias) {
        console.warn('insertarIncidencias: no hay datos (undefined/null)');
        contenedor.innerHTML = '';
        return;
    }

    if (!Array.isArray(incidencias)) {
        console.warn('insertarIncidencias: datos no son array, intentando convertir', incidencias);
        incidencias = [incidencias];
    }

    contenedor.innerHTML = '';
    incidencias.forEach(incidencia => {
        const card = new IncidenciaCard(incidencia).render();
        contenedor.appendChild(card);
    });
}


/*========================================================================
 FUNCIONAMIENTO POP-UPS
 ========================================================================*/

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
    
    // ⚠️ CAMBIO PRINCIPAL: Usamos GestionIncidenciasFake y la nueva ruta /filtradas
    const logicaIncidencias = new GestionIncidenciasFake();
    
    // Llamamos al nuevo método (obtenerIncidenciasFiltradas) que apunta a la ruta autenticada
    // que filtra por rol (admin o tecnico).
    logicaIncidencias.obtenerIncidenciasFiltradas()
        .then(incidencias => {
            console.log("Datos filtrados por rol recibidos del backend:", incidencias); // Para depurar
            
            // Insertamos las tarjetas
            insertarIncidencias(incidencias);
            
            // Configuramos los eventos después de que las tarjetas se han insertado
            configurarEventosIncidencias();
        })
        .catch(err => {
            console.error('Error cargando incidencias filtradas:', err);
            // Mostrar un mensaje de error o limpiar el contenedor
            insertarIncidencias([]);
            // Opcional: mostrar un mensaje de error visible al usuario si no pudo autenticar o cargar datos
            const contenedor = document.getElementById('grid-incidencias');
            if (contenedor) {
                contenedor.innerHTML = '<p class="error-carga">No se pudieron cargar las incidencias. Por favor, inicie sesión con el rol apropiado.</p>';
            }
        });
});