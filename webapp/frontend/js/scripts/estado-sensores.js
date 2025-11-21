import { EstadoSensoresFake } from '../logica_fake/estado_sensores_fake.js';

// -------------------------------------
// Clase que representa la tarjeta
// -------------------------------------
class BikeCard {
    constructor({ id, estado, ultimaActualizacion, parada }) {
        this.id = id;
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
});

// -------------------------------------
// FILTRADO GENERAL (usar allBikes en lugar de demoData)
// -------------------------------------
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

    // Orden final (dañada → activa → desactivado)
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
