/**
 * Crea la clase  una tarjeta de incidencia.
 * @param {object} datos - Objeto con los datos de la incidencia.
 * @param {string} datos.titulo - El título de la incidencia.
 * @param {string} datos.tiempo - El tiempo transcurrido (e.g., "Hace: 5min").
 * @param {string} datos.fuente - La fuente de la incidencia (e.g., "Web").
 * @param {boolean} datos.esResuelto - True si la incidencia está resuelta.
 * @returns {HTMLElement} El elemento div.tarjeta-incidencia creado.
 */
export class IncidenciaCard {
    constructor({ titulo, tiempo, fuente, esResuelto = false }) {
        this.titulo = titulo || 'Incidencia';
        this.tiempo = tiempo || 'Hace: ahora';
        this.fuente = fuente || '';
        this.esResuelto = !!esResuelto;
    }

    /* Crea y devuelve el elemento DOM de la tarjeta de incidencia. */
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