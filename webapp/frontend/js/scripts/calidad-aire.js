import { CalidadAireFake } from '../logica_fake/calidad_aire_fake.js';

// -------------------------------
// SVGs
// -------------------------------

// 1. Buena
const svgGood = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#4CAF50">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM165.4 321.9c20.4 28 53.4 46.1 90.6 46.1s70.2-18.1 90.6-46.1c7.8-10.7 22.8-13.1 33.5-5.3s13.1 22.8 5.3 33.5C356.3 390 309.2 416 256 416s-100.3-26-129.4-65.9c-7.8-10.7-5.4-25.7 5.3-33.5s25.7-5.4 33.5 5.3zM144 208a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zm192-32a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/>
</svg>`;

// 2. Mala
const svgModerate = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#ffcc00">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM176 176a32 32 0 1 1 0 64 32 32 0 1 1 0-64zm128 32a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zM176 320l160 0c13.3 0 24 10.7 24 24s-10.7 24-24 24l-160 0c-13.3 0-24-10.7-24-24s10.7-24 24-24z"/>
</svg>`;

// 3. Poco saludable
const svgBad = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="#e53935">
<path d="M256 512a256 256 0 1 0 0-512 256 256 0 1 0 0 512zm90.6-113.9c-20.4-28-53.4-46.1-90.6-46.1s-70.2 18.1-90.6 46.1c-7.8 10.7-22.8 13.1-33.5 5.3s-13.1-22.8-5.3-33.5C155.7 330 202.8 304 256 304s100.3 26 129.4 65.9c7.8 10.7 5.4 25.7-5.3 33.5s-25.7 5.4-33.5-5.3zM144 208a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zm192-32a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/>
</svg>`;

// -------------------------------
// APARIENCIA SEGÚN AQI
// -------------------------------

// Obtener placa_id del localStorage
const placa_id = localStorage.getItem('placa_id') || "005d0194-d3f0-4eea-be1f-5a9b4ab39e05";

const numberEl = document.getElementById("aqi-number");
const textEl = document.getElementById("aqi-text");
const descEl = document.getElementById("aqi-description");
const iconEl = document.getElementById("aqi-icon");

const logicaAire = new CalidadAireFake();

// Función para actualizar la UI
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

// Cargar AQI al iniciar
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const resultado = await logicaAire.obtenerAQI(placa_id);
        actualizarUI(resultado.aqi);
        
        // Cargar gráfico con histórico
        await cargarGrafico(placa_id);
    } catch (error) {
        console.error('Error al obtener AQI:', error);
        numberEl.textContent = "N/A";
        textEl.textContent = "Error";
        descEl.textContent = "No se pudo obtener la información de calidad del aire.";
    }
});

// Función para formatear hora desde fecha ISO
function formatearHora(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.getHours().toString().padStart(2, '0') + ':' + 
           fecha.getMinutes().toString().padStart(2, '0');
}

// Función para obtener color según valor
function getColorAQI(valor) {
    if (valor <= 49) return "#4CAF50";
    if (valor <= 99) return "#ffcc00";
    return "#e53935";
}

// Función para calcular resumen de los datos
function calcularResumen(mediciones) {
    const valores = mediciones.map(m => m.aqi);
    const promedio = Math.round(valores.reduce((a, b) => a + b, 0) / valores.length);
    const maximo = Math.max(...valores);
    const minimo = Math.min(...valores);
    
    return {
        promedio,
        maximo,
        minimo,
        total_mediciones: valores.length
    };
}

// Función para actualizar el resumen diario
function actualizarResumenDiario(datos) {
    const resumenEl = document.getElementById('resumen-diario');
    if (resumenEl) {
        resumenEl.innerHTML = `
            <div class="resumen-item">
                <span class="resumen-label">Promedio</span>
                <span class="resumen-valor" style="color: ${getColorAQI(datos.promedio)}">${datos.promedio}</span>
            </div>
            <div class="resumen-item">
                <span class="resumen-label">Máximo</span>
                <span class="resumen-valor" style="color: ${getColorAQI(datos.maximo)}">${datos.maximo}</span>
            </div>
            <div class="resumen-item">
                <span class="resumen-label">Mínimo</span>
                <span class="resumen-valor" style="color: ${getColorAQI(datos.minimo)}">${datos.minimo}</span>
            </div>
            <div class="resumen-item">
                <span class="resumen-label">Mediciones</span>
                <span class="resumen-valor">${datos.total_mediciones}</span>
            </div>
        `;
    }
}

// Variable para guardar la instancia del gráfico
let co2Chart = null;

// Función para cargar y mostrar el gráfico
async function cargarGrafico(placa_id) {
    try {
        const mediciones = await logicaAire.obtenerHistorico24h(placa_id);
        
        // Preparar datos
        const horas = mediciones.map(m => formatearHora(m.fecha_hora));
        const valores = mediciones.map(m => m.aqi);
        const colores = valores.map(v => getColorAQI(v));
        
        // Destruir gráfico anterior si existe
        if (co2Chart) {
            co2Chart.destroy();
        }
        
        // Crear gráfico
        const ctx = document.getElementById('co2Chart').getContext('2d');
        co2Chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: horas,
                datasets: [{
                    label: 'AQI',
                    data: valores,
                    borderColor: '#555',           
                    borderWidth: 2,
                    fill: false,
                    pointBackgroundColor: colores,
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
                        },
                        title: {
                            display: true,
                            text: 'Índice de Calidad del Aire (AQI)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Hora del día'
                        }
                    }
                }
            }
        });
        
        // Calcular y mostrar resumen
        const resumen = calcularResumen(mediciones);
        actualizarResumenDiario(resumen);
        
    } catch (error) {
        console.error('Error al cargar gráfico:', error);
        document.getElementById('resumen-diario').innerHTML = 
            '<p class="error-message">Error al cargar los datos del gráfico</p>';
    }
}
