// -------------------------------------
// Clase que representa la tarjeta
// -------------------------------------
class BikeCard {
    constructor({ id, estado, ultimaActualizacion, parada, problemas }) {
        this.id = id;
        this.estado = estado;
        this.ultimaActualizacion = ultimaActualizacion;
        this.parada = parada;
        this.problemas = problemas; // TODO: lógica para el siguiente sprint
    }

    render() {
        const card = document.createElement("article");
        card.classList.add("bike-card");

        const stateClass = getStateClass(this.estado);
        if (stateClass) card.classList.add(stateClass);

        if (this.problemas > 0) {
            const badge = document.createElement("span");
            badge.classList.add("problem-badge");
            badge.textContent = `${this.problemas} Problema${this.problemas > 1 ? "s" : ""}`;
            card.appendChild(badge);
        }

        card.innerHTML += `
            <div class="bike-title">Bici ${this.id}</div>
            <p class="bike-info"><b>Último dato:</b> ${this.ultimaActualizacion}</p>
            <p class="bike-info"><b>Estado:</b> ${this.estado}</p>
            <p class="bike-info"><b>Parada:</b> ${this.parada}</p>
        `;

        return card;
    }
}

// -------------------------------------
// Datos de prueba (simulan respuesta del backend)
// TODO: sustituir por fetch() al back
// -------------------------------------
const demoData = [
    { id: "01", estado: "Dañado", ultimaActualizacion: "19 horas", parada: "Ciutat Vella"},
    { id: "02", estado: "Funcional", ultimaActualizacion: "5 min", parada: "Ayora"},
    { id: "03", estado: "Funcional", ultimaActualizacion: "4 horas", parada: "Alboraya"},
    { id: "04", estado: "Desactivado", ultimaActualizacion: "24 horas", parada: "Malvarrosa"},
    { id: "05", estado: "Dañado", ultimaActualizacion: "19 horas", parada: "Ruzafa" }
];

// -------------------------------------
// Render inicial
// -------------------------------------
const bikeList = document.getElementById("bikeList");
const searchInput = document.getElementById("searchInput");
const stateButtons = document.querySelectorAll(".state-btn");

let searchText = "";
let selectedState = null; // null -> todas

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
        case "danado":
            return "danado";
        case "desactivado":
            return "desactivado";
        default:
            return ""; // funcional
    }
}

function orderBikes(data) {
    const order = {
        danado: 1,
        funcional: 2,
        desactivado: 3
    };

    return data.sort((a, b) => {
        return order[normalizeState(a.estado)] - order[normalizeState(b.estado)];
    });
}

// Normaliza el estado para comparaciones por tema tildes y eñes
function normalizeState(estado) {
    return estado
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, ""); // quita tildes
}

// -------------------------------------
// FILTRADO GENERAL
// -------------------------------------
function applyFilters() {
    let filtered = [...demoData];

    // Filtro por texto (ID)
    if (searchText.trim() !== "") {
        filtered = filtered.filter(bike =>
            bike.id.toLowerCase().includes(searchText.toLowerCase())
        );
    }

    // Filtro por estado
    if (selectedState !== null) {
        filtered = filtered.filter(bike =>
            bike.estado.toLowerCase() === selectedState
        );
    }

    // Orden final (dañado → funcional → desactivado)
    filtered = orderBikes(filtered);

    renderBikes(filtered);
}

// -------------------------------------
// EVENTOS: Búsqueda en tiempo real
// -------------------------------------
searchInput.addEventListener("keyup", (e) => {
    searchText = e.target.value;
    applyFilters();
});

// -------------------------------------
// EVENTOS: Botones de estado
// -------------------------------------
stateButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const state = btn.dataset.state;

        if (selectedState === state) {
            selectedState = null;
            stateButtons.forEach(b => b.classList.remove("active"));
        } else {
            selectedState = normalizeState(btn.dataset.state);
            stateButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
        }

        applyFilters();
    });
});

// Render inicial
applyFilters();
