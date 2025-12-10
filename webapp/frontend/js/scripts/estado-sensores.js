import { EstadoSensoresFake } from '../logica_fake/estado_sensores_fake.js';

// -------------------------------------
// Clase que representa la tarjeta
// -------------------------------------
class BikeCard {
    constructor({ id, placa_id, estado, ultimaActualizacion, parada }) {
        this.id = id;
        this.placa_id = placa_id;  // AGREGAR ESTO
        this.estado = estado;
        this.ultimaActualizacion = ultimaActualizacion;
        this.parada = parada;
    }

    render() {
        const card = document.createElement("article");
        card.classList.add("bike-card");

        const stateClass = getStateClass(this.estado);
        if (stateClass) card.classList.add(stateClass);

        card.innerHTML = `
            <div class="bike-title">${this.id}</div>
            <p class="bike-info"><b>Último dato:</b> ${this.ultimaActualizacion}</p>
            <p class="bike-info"><b>Estado:</b> ${this.estado}</p>
            <p class="bike-info"><b>Parada:</b> ${this.parada}</p>
        `;

        // Agregar evento de click para abrir modal - CAMBIAR a this.placa_id
        card.addEventListener('click', () => {
            abrirModalMediciones(this.placa_id);  // CAMBIAR AQUÍ
        });

        return card;
    }
}

// -----------------------------------
// Datos
// -----------------------------------
const bikeList = document.getElementById("bikeList");
const searchInput = document.getElementById("searchInput");
const stateButtons = document.querySelectorAll(".state-btn");

const logicaSensores = new EstadoSensoresFake();

let allBikes = []; // Datos del backend
let searchText = "";
let selectedState = null; // null -> todas
let medicionesActuales = []; // Mediciones mostradas actualmente
let placaIdActual = null; // Placa actual en el modal

// -----------------------------------
// CARGAR DATOS DEL BACKEND
// -----------------------------------
async function cargarBicicletas() {
    try {
        allBikes = await logicaSensores.obtenerBicicletas();
        applyFilters();
    } catch (error) {
        console.error('Error al obtener bicicletas:', error);
        bikeList.innerHTML = '<p class="error-message">Error al cargar los datos de las bicicletas</p>';
    }
}

// Cargar al iniciar
document.addEventListener('DOMContentLoaded', () => {
    cargarBicicletas();
    setupModalEventos();
});

// -----------------------------------
// MODAL DE MEDICIONES
// -----------------------------------
const modal = document.getElementById('modalMediciones');
const btnCerrar = document.getElementById('cerrarModal');
const btnCerrar2 = document.getElementById('btnCerrarModal2');
const btnEliminarAnómalas = document.getElementById('btnEliminarAnómalas');
const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
const filtroFechaInicio = document.getElementById('filtroFechaInicio');
const filtroFechaFin = document.getElementById('filtroFechaFin');
const cuerpoTabla = document.getElementById('cuerpoTabla');

async function abrirModalMediciones(placa_id) {
    placaIdActual = placa_id;
    document.getElementById('modalPlacaId').textContent = placa_id;
    
    try {
        medicionesActuales = await logicaSensores.obtenerMediciones(placa_id);
        mostrarMediciones(medicionesActuales);
        modal.style.display = 'flex';
    } catch (error) {
        console.error('Error al obtener mediciones:', error);
        cuerpoTabla.innerHTML = '<tr><td colspan="5" class="error">Error al cargar mediciones</td></tr>';
        modal.style.display = 'flex';
    }
}

function mostrarMediciones(mediciones) {
    cuerpoTabla.innerHTML = '';
    
    if (mediciones.length === 0) {
        cuerpoTabla.innerHTML = '<tr><td colspan="5" class="sin-datos">No hay mediciones</td></tr>';
        return;
    }
    
    mediciones.forEach(med => {
        const fila = document.createElement('tr');
        if (med.es_anomalo) {
            fila.classList.add('anomalo');
        }
        
        const fecha = new Date(med.fecha_hora);
        const fechaFormato = fecha.toLocaleString('es-ES');
        const estado = med.es_anomalo ? '⚠️ Anómalo' : '✓ Normal';
        
        fila.innerHTML = `
            <td>${fechaFormato}</td>
            <td>${med.tipo}</td>
            <td>${med.valor.toFixed(2)}</td>
            <td>${estado}</td>
            <td>
                <button class="btn-eliminar-med" data-lectura-id="${med.lectura_id}">Eliminar</button>
            </td>
        `;
        
        cuerpoTabla.appendChild(fila);
    });
    
    // Agregar eventos a botones de eliminar
    document.querySelectorAll('.btn-eliminar-med').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const lecturaId = e.target.dataset.lecturaId;
            const valor = mediciones.find(m => m.lectura_id === lecturaId).valor;
            abrirModalConfirmacion(lecturaId, valor);
        });
    });
}

function setupModalEventos() {
    btnCerrar.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    btnCerrar2.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    btnEliminarAnómalas.addEventListener('click', async () => {
        const anomalas = medicionesActuales.filter(m => m.es_anomalo);
        if (anomalas.length === 0) {
            alert('No hay mediciones anómalas para eliminar');
            return;
        }
        
        abrirModalConfirmacion(null, null, anomalas.length);
    });
    
    btnAplicarFiltros.addEventListener('click', async () => {
        const inicio = filtroFechaInicio.value;
        const fin = filtroFechaFin.value;
        
        try {
            const fechaInicio = inicio ? new Date(inicio).toISOString() : null;
            const fechaFin = fin ? new Date(fin).toISOString() : null;
            
            medicionesActuales = await logicaSensores.obtenerMediciones(
                placaIdActual,
                fechaInicio,
                fechaFin
            );
            mostrarMediciones(medicionesActuales);
        } catch (error) {
            console.error('Error al aplicar filtros:', error);
            alert('Error al aplicar filtros');
        }
    });
    
    btnLimpiarFiltros.addEventListener('click', async () => {
        filtroFechaInicio.value = '';
        filtroFechaFin.value = '';
        
        try {
            medicionesActuales = await logicaSensores.obtenerMediciones(placaIdActual);
            mostrarMediciones(medicionesActuales);
        } catch (error) {
            console.error('Error al limpiar filtros:', error);
        }
    });
    
    // Cerrar modal al hacer click fuera
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// -----------------------------------
// MODAL DE CONFIRMACIÓN
// -----------------------------------
const modalConfirmacion = document.getElementById('modalConfirmacion');
const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
const btnCancelarEliminar = document.getElementById('btnCancelarEliminar');
const textoConfirmacion = document.getElementById('textoConfirmacion');

let tipoEliminacion = null; // 'individual', 'anomalas'
let lecturaIdEliminar = null;
let cantidadAnomalas = 0;

function abrirModalConfirmacion(lecturaId, valor, cantidad = null) {
    if (cantidad !== null) {
        // Eliminar todas las anómalas
        tipoEliminacion = 'anomalas';
        cantidadAnomalas = cantidad;
        textoConfirmacion.textContent = `¿Está seguro de que desea eliminar ${cantidad} medición(es) anómala(s)?`;
    } else {
        // Eliminar una individual
        tipoEliminacion = 'individual';
        lecturaIdEliminar = lecturaId;
        textoConfirmacion.textContent = `¿Está seguro de que desea eliminar la medición con valor ${valor}?`;
    }
    
    modalConfirmacion.style.display = 'flex';
}

btnConfirmarEliminar.addEventListener('click', async () => {
    try {
        if (tipoEliminacion === 'individual') {
            await logicaSensores.eliminarMedicion(lecturaIdEliminar);
        } else if (tipoEliminacion === 'anomalas') {
            await logicaSensores.eliminarMedicionesAnómalas(placaIdActual);
        }
        
        // Recargar mediciones
        medicionesActuales = await logicaSensores.obtenerMediciones(placaIdActual);
        mostrarMediciones(medicionesActuales);
        
        modalConfirmacion.style.display = 'none';
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error al eliminar la(s) medición(es)');
    }
});

btnCancelarEliminar.addEventListener('click', () => {
    modalConfirmacion.style.display = 'none';
});

// -----------------------------------
// FILTRADO GENERAL
// -----------------------------------
function applyFilters() {
    let filtered = [...allBikes];

    // Filtro por texto (ID)
    if (searchText.trim() !== "") {
        filtered = filtered.filter(bike =>
            bike.id.toLowerCase().includes(searchText.toLowerCase())
        );
    }

    // Filtro por estado
    if (selectedState !== null) {
        filtered = filtered.filter(bike =>
            normalizeState(bike.estado) === selectedState
        );
    }

    // Orden final (dañada → activa → desactivada)
    filtered = orderBikes(filtered);

    renderBikes(filtered);
}

function renderBikes(data) {
    bikeList.innerHTML = "";
    data.forEach(bike => {
        const card = new BikeCard(bike).render();
        bikeList.appendChild(card);
    });
}

function getStateClass(estado) {
    const norm = normalizeState(estado);

    switch (norm) {
        case "danada":
            return "danada";
        case "desactivada":
            return "desactivada";
        case "activa":
            return "activa";
        default:
            return "";
    }
}

function orderBikes(data) {
    const order = {
        danada: 1,
        activa: 2,
        desactivada: 3
    };

    return data.sort((a, b) => {
        return (order[normalizeState(a.estado)] || 99) - (order[normalizeState(b.estado)] || 99);
    });
}

// Normaliza el estado para comparaciones
function normalizeState(estado) {
    return estado
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

// -----------------------------------
// EVENTOS: Búsqueda en tiempo real
// -----------------------------------
searchInput.addEventListener("keyup", (e) => {
    searchText = e.target.value;
    applyFilters();
});

// -----------------------------------
// EVENTOS: Botones de estado
// -----------------------------------
stateButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const state = normalizeState(btn.dataset.state);

        if (selectedState === state) {
            selectedState = null;
            stateButtons.forEach(b => b.classList.remove("active"));
        } else {
            selectedState = state;
            stateButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
        }

        applyFilters();
    });
});
