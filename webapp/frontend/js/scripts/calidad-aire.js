import { CalidadAireFake } from '../logica_fake/calidad_aire_fake.js';

// ------------------------------------------
// Decodificador JWT (sin librerías externas)
// ------------------------------------------
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error decodificando JWT:', error);
        return null;
    }
}

// SVGs
const svgGood = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#4CAF50">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM165.4 321.9c20.4 28 53.4 46.1 90.6 46.1s70.2-18.1 90.6-46.1c7.8-10.7 22.8-13.1 33.5-5.3s13.1 22.8 5.3 33.5C356.3 390 309.2 416 256 416s-100.3-26-129.4-65.9c-7.8-10.7-5.4-25.7 5.3-33.5s25.7-5.4 33.5 5.3zM144 208a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zm192-32a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/>
</svg>`;

const svgModerate = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#ffcc00">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM176 176a32 32 0 1 1 0 64 32 32 0 1 1 0-64zm128 32a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zM176 320l160 0c13.3 0 24 10.7 24 24s-10.7 24-24 24l-160 0c-13.3 0-24-10.7-24-24s10.7-24 24-24z"/>
</svg>`;

const svgBad = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#e53935">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zm90.6-113.9c-20.4-28-53.4-46.1-90.6-46.1s-70.2 18.1-90.6 46.1c-7.8 10.7-22.8 13.1-33.5 5.3s-13.1-22.8-5.3-33.5C155.7 330 202.8 304 256 304s100.3 26 129.4 65.9c7.8 10.7 5.4 25.7-5.3 33.5s-25.7 5.4-33.5-5.3zM144 208a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zm192-32a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/>
</svg>`;

// elementos del DOM
const numberEl = document.getElementById("aqi-number");
const textEl = document.getElementById("aqi-text");
const descEl = document.getElementById("aqi-description");
const iconEl = document.getElementById("aqi-icon");
const h2Section = document.querySelector('.co2-section h2');

const logicaAire = new CalidadAireFake();

// Función para actualizar la UI con AQI
function actualizarUI(aqi) {
    numberEl.textContent = aqi;

    if (aqi <= 49) {
        numberEl.style.color = "#4CAF50";
        textEl.textContent = "Buena";
        descEl.textContent = "La calidad del aire es satisfactoria y la contaminación del aire presenta poco o ningún riesgo.";
        iconEl.innerHTML = svgGood;
    } else if (aqi <= 99) {
        numberEl.style.color = "#ffcc00";
        textEl.textContent = "Mala";
        descEl.textContent = "El aire presenta niveles elevados de contaminación. Las personas sensibles pueden experimentar efectos.";
        iconEl.innerHTML = svgModerate;
    } else {
        numberEl.style.color = "#e53935";
        textEl.textContent = "Poco saludable";
        descEl.textContent = "La calidad del aire es dañina especialmente para grupos sensibles. Evite la exposición prolongada.";
        iconEl.innerHTML = svgBad;
    }
}

// Función para formatear fecha a formato legible
function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para obtener color según AQI
function getColorAQI(valor) {
    if (valor <= 49) return "#4CAF50";
    if (valor <= 99) return "#ffcc00";
    return "#e53935";
}

// Función para actualizar título y mostrar fechas del trayecto
function actualizarTituloConFechas(trayecto) {
    const fechaInicio = formatearFecha(trayecto.fecha_inicio);
    const fechaFin = trayecto.fecha_fin ? formatearFecha(trayecto.fecha_fin) : "En progreso";
    
    if (h2Section) {
        h2Section.innerHTML = `Niveles del Aire en el último trayecto<br><small style="font-size: 0.8em; color: #666;">Del ${fechaInicio} al ${fechaFin}</small>`;
    }
}

// Función para mostrar mensaje de error
function mostrarMensajeError(mensaje) {
    numberEl.textContent = "No disponible";
    textEl.textContent = "Sin trayectos";
    descEl.textContent = mensaje;
    iconEl.innerHTML = '';
    
    const resumenEl = document.getElementById('resumen-diario');
    if (resumenEl) {
        resumenEl.innerHTML = `<p style="text-align: center; color: #666; padding: 2rem;">${mensaje}</p>`;
    }
    
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        chartContainer.style.display = 'none';
    }
}

// Cargar AQI y trayecto al iniciar
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const token = localStorage.getItem('token');
        
        if (!token) {
            mostrarMensajeError('Por favor, inicia sesión para ver tu calidad de aire.');
            return;
        }

        // Obtener el último trayecto completado del usuario
        const trayecto = await logicaAire.obtenerUltimoTrayecto(token);
        
        if (!trayecto) {
            mostrarMensajeError('No hay trayectos completados.');
            return;
        }

        // Actualizar UI con el AQI promediado
        actualizarUI(trayecto.aqi_promedio);
        actualizarTituloConFechas(trayecto);
        
        // Cargar gráfico con mediciones del trayecto
        console.log(trayecto);
        
        await cargarGraficoTrayecto(trayecto);

    } catch (error) {
        console.error('Error al obtener trayecto:', error);
        mostrarMensajeError('No hay trayectos disponibles o error en la carga.');
    }
});

// Variable para el gráfico
let co2Chart = null;

// Función para formatear hora desde fecha ISO
function formatearHora(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.getHours().toString().padStart(2, '0') + ':' + 
           fecha.getMinutes().toString().padStart(2, '0');
}

// Función para cargar gráfico del trayecto
async function cargarGraficoTrayecto(trayecto) {
    try {
        const ctx = document.getElementById('co2Chart');
        if (!ctx) return;
        
        const canvasElement = ctx.getContext('2d');
        
        if (co2Chart) {
            co2Chart.destroy();
        }

        // Obtener mediciones PM2.5 reales para el trayecto
        let mediciones = [];
        try {
            const url = `/api/v1/trayectos/${trayecto.trayecto_id}/mediciones`;
            mediciones = await logicaAire.peticionario.hacerPeticionRest('GET', url);
        } catch (error) {
            console.warn('No se pudieron cargar mediciones reales, usando placeholder:', error);
            mediciones = []; // Usar array vacío si no hay mediciones
        }

        // Preparar datos para el gráfico
        const labels = mediciones.length > 0 
            ? mediciones.map((m, idx) => formatearHora(m.fecha_hora))
            : ['Sin datos'];
        
        const aqiValues = mediciones.length > 0 
            ? mediciones.map(m => m.aqi)
            : [0];

        const pointColors = mediciones.length > 0
            ? mediciones.map(m => getColorAQI(m.aqi))
            : ['#999'];

        co2Chart = new Chart(canvasElement, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'AQI del Trayecto',
                    data: aqiValues,
                    borderColor: '#555',           
                    borderWidth: 2,
                    fill: false,
                    pointBackgroundColor: pointColors,
                    pointRadius: 6,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        min: 0,
                        max: 300,
                        ticks: {
                            stepSize: 50
                        }
                    }
                }
            }
        });

        // Actualizar resumen con datos reales del trayecto
        const resumenEl = document.getElementById('resumen-diario');
        if (resumenEl) {
            resumenEl.innerHTML = `
                <div class="resumen-item">
                    <span class="resumen-label">Total Mediciones</span>
                    <span class="resumen-valor">${trayecto.mediciones_count}</span>
                </div>
                <div class="resumen-item">
                    <span class="resumen-label">AQI Promedio</span>
                    <span class="resumen-valor" style="color: ${getColorAQI(trayecto.aqi_promedio)}">${trayecto.aqi_promedio}</span>
                </div>
                <div class="resumen-item">
                    <span class="resumen-label">Distancia Total</span>
                    <span class="resumen-valor">${(trayecto.distancia_total / 1000).toFixed(2)} km</span>
                </div>
            `;
        }

    } catch (error) {
        console.error('Error al cargar gráfico:', error);
    }
}
