// -------------------------------------
// Clase que representa la tarjeta
// -------------------------------------
class BikeCard {
    constructor({ id, estado, ultimaActualizacion, parada, sensores, problemas }) {
        this.id = id;
        this.estado = estado;
        this.ultimaActualizacion = ultimaActualizacion;
        this.parada = parada;
        this.sensores = sensores;
        this.problemas = problemas;
    } // TODO: cambiar logica segun diseños bbdd

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
            <div class="sensor-tags">
                ${this.sensores.map(s => `<span class="tag">${s}</span>`).join("")}
            </div>
        `;

        return card;
    }
}

// -------------------------------------
// Datos de prueba (simulan respuesta del backend)
// TODO: sustituir por fetch() al back
// -------------------------------------
const demoData = [
    { id: "01", estado: "Dañado", ultimaActualizacion: "19 horas", parada: "Ciutat Vella", sensores: ["Placa", "Batería", "CO2"], problemas: 3 },
    { id: "02", estado: "Funcional", ultimaActualizacion: "5 min", parada: "Ayora", sensores: ["Placa", "Batería", "CO2"], problemas: 0 },
    { id: "03", estado: "Funcional", ultimaActualizacion: "4 horas", parada: "Alboraya", sensores: ["Placa", "Batería"], problemas: 0 },
    { id: "04", estado: "Desactivado", ultimaActualizacion: "24 horas", parada: "Malvarrosa", sensores: ["Placa", "Batería", "CO2"], problemas: 0 },
    { id: "05", estado: "Dañado", ultimaActualizacion: "19 horas", parada: "Ruzafa", sensores: ["Placa", "Batería", "CO2"], problemas: 1 }
];


// -------------------------------------
// Render inicial
// -------------------------------------
const bikeList = document.getElementById("bikeList");

function renderBikes(data) {
    bikeList.innerHTML = "";
    data.forEach(bike => {
        const card = new BikeCard(bike).render();
        bikeList.appendChild(card);
    });
}

function getStateClass(estado) {
    switch (estado.toLowerCase()) {
        case "dañado":
            return "danado";
        case "desactivado":
            return "desactivado";
        default:
            return ""; // funcional → color por defecto
    }
}

function orderBikes(data) {
    const order = {
        "dañado": 1,
        "funcional": 2,
        "desactivado": 3
    };

    return data.sort((a, b) => {
        return order[a.estado.toLowerCase()] - order[b.estado.toLowerCase()];
    });
}

renderBikes(orderBikes(demoData));

// -------------------------------------
// TODO: Implementar filtros y fetch al back
// -------------------------------------
