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

const logicaIncidencias = new GestionIncidenciasFake();

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
        // Guardar el id de la incidencia en dataset para poder usarlo en acciones (cambiar estado)
        if (incidencia.incidencia_id) {
            card.dataset.incidenciaId = incidencia.incidencia_id;
        }
        // Guardar la fecha original (ISO) para permitir ordenamiento
        if (incidencia.fecha_reporte) {
            card.dataset.fecha = incidencia.fecha_reporte;
        }
        // Guardar estado resuelto/no resuelto para filtros
        if (typeof incidencia.esResuelto !== 'undefined') {
            card.dataset.resuelto = incidencia.esResuelto ? 'true' : 'false';
        }
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
    const incidenciaId = tarjeta.dataset.incidenciaId || null;

    return {
        titulo: tituloIncidencia,
        tiempo: tiempo,
        fuente: fuente,
        esResuelto: esResuelto,
        estadoTexto: estadoTexto,
        actionText: actionText,
        idUsuario: idUsuarioUnico,
        incidenciaId: incidenciaId
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
                const nuevoEstado = datosIncidencia.esResuelto ? 'cerrado' : 'resuelto';
                const idToUse = datosIncidencia.incidenciaId || tarjeta.dataset.incidenciaId || null;
                if (idToUse) {
                    logicaIncidencias.cambiarEstadoIncidencia(idToUse, nuevoEstado)
                        .then(resp => {
                            console.log('Cambio de estado OK:', resp);
                        })
                        .catch(err => {
                            console.error('Error cambiando estado:', err);
                        });
                } else {
                    console.warn('No se encontró incidencia_id para cambiar estado');
                }
                incidenciaPopup.cerrarPopup(); // Cierra el pop-up después de la acción
            });


            incidenciaPopup.abrirPopup();
        });
    });
}

// Configura la búsqueda en la barra de búsqueda: filtra tarjetas por título (case-insensitive)
function configurarBusqueda() {
    const input = document.querySelector('.campo-busqueda');
    const contenedor = document.getElementById('grid-incidencias');
    if (!input || !contenedor) return;

    // Elemento para mostrar cuando no hay resultados
    let noResultsEl = document.querySelector('.no-results-message');
    if (!noResultsEl) {
        noResultsEl = document.createElement('p');
        noResultsEl.className = 'no-results-message';
        noResultsEl.style.display = 'none';
        noResultsEl.textContent = 'No se encontraron incidencias que coincidan.';
        contenedor.parentNode.insertBefore(noResultsEl, contenedor.nextSibling);
    }

    const filterFn = (query) => {
        const q = (query || '').trim().toLowerCase();
        const tarjetas = Array.from(contenedor.querySelectorAll('.tarjeta-incidencia'));
        let visibleCount = 0;
        tarjetas.forEach(tarjeta => {
            const titulo = tarjeta.querySelector('.titulo-incidencia')?.textContent?.toLowerCase() || '';
            const fuente = tarjeta.querySelector('.detalle-incidencia.fuente')?.textContent?.toLowerCase() || '';
            // Coincidir si el query está en el título o en la fuente
            const match = q === '' || titulo.includes(q) || fuente.includes(q);
            tarjeta.style.display = match ? '' : 'none';
            if (match) visibleCount += 1;
        });

        noResultsEl.style.display = visibleCount === 0 ? '' : 'none';
    };

    // Filtrado en tiempo real
    input.addEventListener('input', (e) => {
        filterFn(e.target.value);
    });

    // Soporte tecla Enter para buscar (prevenir submit si estuviera en form)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            filterFn(e.target.value);
        }
    });
}

// Ordenamiento: por fecha (dataset.fecha). masRecientes=true => más recientes primero
function ordenarTarjetas(masRecientes = true) {
    const contenedor = document.getElementById('grid-incidencias');
    if (!contenedor) return;

    const tarjetas = Array.from(contenedor.querySelectorAll('.tarjeta-incidencia'));
    // Si no hay fechas, no hacemos nada
    const anyFecha = tarjetas.some(t => t.dataset && t.dataset.fecha);
    if (!anyFecha) return;

    tarjetas.sort((a, b) => {
        const ta = a.dataset.fecha ? new Date(a.dataset.fecha).getTime() : 0;
        const tb = b.dataset.fecha ? new Date(b.dataset.fecha).getTime() : 0;
        return masRecientes ? tb - ta : ta - tb;
    });

    tarjetas.forEach(t => contenedor.appendChild(t));
}

function configurarOrdenamiento() {
    const botones = document.querySelectorAll('.botones-filtro .boton-filtro');
    if (!botones || botones.length < 2) return;
    const btnUp = botones[0];
    const btnDown = botones[1];

    btnUp.title = 'Mostrar incidencias más recientes';
    btnDown.title = 'Mostrar incidencias más antiguas';

    btnUp.addEventListener('click', () => {
        ordenarTarjetas(true);
        btnUp.classList.add('active-sort');
        btnDown.classList.remove('active-sort');
    });

    btnDown.addEventListener('click', () => {
        ordenarTarjetas(false);
        btnDown.classList.add('active-sort');
        btnUp.classList.remove('active-sort');
    });
}

// Aplica el filtro por estado: 'all' | 'resueltas' | 'no_resueltas'
function aplicarFiltroEstado(estado) {
    const contenedor = document.getElementById('grid-incidencias');
    if (!contenedor) return;
    const tarjetas = Array.from(contenedor.querySelectorAll('.tarjeta-incidencia'));

    tarjetas.forEach(tarjeta => {
        // Si la tarjeta está ya oculta por la búsqueda, respetar eso (no sobreescribir si display 'none' por búsqueda)
        const actualmenteOcultaPorBusqueda = tarjeta.classList.contains('hidden-by-search');
        const esResuelto = tarjeta.dataset.resuelto === 'true';

        let mostrar = true;
        if (estado === 'resueltas') mostrar = !!esResuelto;
        else if (estado === 'no_resueltas') mostrar = !esResuelto;

        // Si la búsqueda ya la ocultó, mantenla oculta; en otro caso aplicar mostrar/ocultar según filtro
        if (actualmenteOcultaPorBusqueda) {
            tarjeta.style.display = 'none';
        } else {
            tarjeta.style.display = mostrar ? '' : 'none';
        }
    });
}

// Configura el menú de filtro que aparece al pulsar el botón de filtro
function configurarFiltro() {
    const contenedorBotones = document.querySelector('.botones-filtro');
    if (!contenedorBotones) return;
    const botones = contenedorBotones.querySelectorAll('.boton-filtro');
    const btnFiltro = botones && botones[2] ? botones[2] : null;
    if (!btnFiltro) return;

    // Crear el menú flotante (si no existe)
    let menu = document.querySelector('.filtro-menu');
    if (!menu) {
        menu = document.createElement('div');
        menu.className = 'filtro-menu';
        // estilos inline mínimos para que sea visible
        menu.style.position = 'absolute';
        menu.style.background = '#fff';
        menu.style.border = '1px solid rgba(0,0,0,0.12)';
        menu.style.padding = '6px';
        menu.style.boxShadow = '0 2px 6px rgba(0,0,0,0.12)';
        menu.style.zIndex = '9999';
        menu.style.display = 'none';

        const opcAll = document.createElement('button');
        opcAll.textContent = 'Mostrar todas';
        opcAll.className = 'filtro-opc';
        opcAll.style.display = 'block';
        opcAll.style.width = '100%';
        opcAll.style.marginBottom = '4px';

        const opcNo = document.createElement('button');
        opcNo.textContent = 'Sólo no resueltas';
        opcNo.className = 'filtro-opc';
        opcNo.style.display = 'block';
        opcNo.style.width = '100%';
        opcNo.style.marginBottom = '4px';

        const opcSi = document.createElement('button');
        opcSi.textContent = 'Sólo resueltas';
        opcSi.className = 'filtro-opc';
        opcSi.style.display = 'block';
        opcSi.style.width = '100%';

        menu.appendChild(opcAll);
        menu.appendChild(opcNo);
        menu.appendChild(opcSi);
        document.body.appendChild(menu);

        // Listeners
        opcAll.addEventListener('click', () => { aplicarFiltroEstado('all'); menu.style.display = 'none'; });
        opcNo.addEventListener('click', () => { aplicarFiltroEstado('no_resueltas'); menu.style.display = 'none'; });
        opcSi.addEventListener('click', () => { aplicarFiltroEstado('resueltas'); menu.style.display = 'none'; });
    }

    // Mostrar/ocultar menú al pulsar el botón
    btnFiltro.addEventListener('click', (e) => {
        e.stopPropagation();
        // posicionar debajo del botón
        const rect = btnFiltro.getBoundingClientRect();
        menu.style.top = `${rect.bottom + window.scrollY + 6}px`;
        menu.style.left = `${rect.left + window.scrollX}px`;
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    });

    // Cerrar cuando se hace click fuera
    document.addEventListener('click', (e) => {
        if (menu && e.target !== btnFiltro && !menu.contains(e.target)) {
            menu.style.display = 'none';
        }
    });
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    
    
    // Llamamos al nuevo método (obtenerIncidenciasFiltradas) que apunta a la ruta autenticada
    // que filtra por rol (admin o tecnico).
    logicaIncidencias.obtenerIncidenciasFiltradas()
        .then(incidencias => {
            console.log("Datos filtrados por rol recibidos del backend:", incidencias); // Para depurar
            
            // Insertamos las tarjetas
            insertarIncidencias(incidencias);
            
            // Configuramos los eventos después de que las tarjetas se han insertado
            configurarEventosIncidencias();
            // Configurar búsqueda en la barra
            configurarBusqueda();
            // Configurar ordenamiento por fecha
            configurarOrdenamiento();
            // Configurar filtro por estado
            configurarFiltro();
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