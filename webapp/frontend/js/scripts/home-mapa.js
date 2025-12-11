// frontend/js/scripts/home-mapa.js
import { MapaFake } from '../logica_fake/mapa_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    // =============== MAPA BÁSICO ==========================
    // 用 Gandia 的中心，让它和 mapas.html 一致
    const map = L.map('map', {
        zoomControl: true
    }).setView([39.0000, -0.1650], 14);

    const baseLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        crossOrigin: ''
    }).addTo(map);

    const mapaFake = new MapaFake();

    // =============== CAPAS POR GAS ========================
    // keys = tipo que espera backend / MapaFake
    const gases = {
        pm2_5: {
            nombre: 'Gas 1 (PM2.5)',
            layerGroup: L.layerGroup().addTo(map)
        },
        pm10: {
            nombre: 'Gas 2 (PM10)',
            layerGroup: L.layerGroup().addTo(map)
        },
        no2: {
            nombre: 'Gas 3 (NO₂)',
            layerGroup: L.layerGroup().addTo(map)
        },
        o3: {
            nombre: 'O₃',
            layerGroup: L.layerGroup().addTo(map)
        }
    };

    // Capa de puestos de bicis
    const capaBicis = L.layerGroup().addTo(map);

    // =============== CONTROL DE CAPAS =====================
    const overlays = {};
    Object.values(gases).forEach(cfg => {
        overlays[cfg.nombre] = cfg.layerGroup;
    });
    overlays['Puestos de bicicletas'] = capaBicis;

    L.control.layers({ openstreetmap: baseLayer }, overlays, {
        collapsed: false
    }).addTo(map);

    // =============== PARÁMETROS HEATMAP ===================
    // 比你原来的稍微大一点，效果更明显
    const FIXED_RADIUS = 60;
    const FIXED_BLUR = 20;

    function fixedIntensity(color) {
        if (color === 'verde') return 25;
        if (color === 'amarillo') return 40;
        return 60; // rojo
    }

    // =============== CARGA INICIAL ========================
    refrescarTodo();
    // 如果希望移动地图时重新加载，可以打开：
    // map.on('moveend', refrescarTodo);

    // =============== FUNCIONES PRINCIPALES ================

    async function refrescarTodo() {
        const hoy = new Date().toISOString().split('T')[0];

        // 用当前地图的 bounds，当你以后想放大缩小也能自适应
        const bounds = map.getBounds();
        const latMin = bounds.getSouth();
        const latMax = bounds.getNorth();
        const lonMin = bounds.getWest();
        const lonMax = bounds.getEast();

        // 清空旧的 capas
        Object.values(gases).forEach(cfg => cfg.layerGroup.clearLayers());
        capaBicis.clearLayers();

        // 4 个气体并行加载
        await Promise.all([
            cargarGas('pm2_5', gases.pm2_5, hoy, latMin, lonMin, latMax, lonMax),
            cargarGas('pm10',  gases.pm10,  hoy, latMin, lonMin, latMax, lonMax),
            cargarGas('no2',   gases.no2,   hoy, latMin, lonMin, latMax, lonMax),
            cargarGas('o3',    gases.o3,    hoy, latMin, lonMin, latMax, lonMax)
        ]);

        // 自行车（如果后端还没这个 endpoint，会在 console 打一个 error，不会影响地图）
        cargarBicis();
    }

    /**
     * Carga un tipo de gas (pm2_5, pm10, no2, o3) en su LayerGroup usando MapaFake.
     */
    async function cargarGas(tipo, cfg, dia, latMin, lonMin, latMax, lonMax) {
        try {
            const respuesta = await mapaFake.obtenerMapa(
                tipo,
                dia,
                latMin,
                lonMin,
                latMax,
                lonMax
            );

            console.log('Gas', tipo, 'respuesta:', respuesta);

            const puntos = extraerPuntosDeHoraActual(respuesta);
            if (!puntos.length) return;

            const heatPoints = puntos.map(p => [
                p.lat,
                p.lng,
                fixedIntensity(p.color)
            ]);

            const heatLayer = L.heatLayer(heatPoints, {
                radius: FIXED_RADIUS,
                blur: FIXED_BLUR,
                gradient: {
                    0.0: 'green',
                    0.5: 'yellow',
                    1.0: 'red'
                }
            });

            cfg.layerGroup.addLayer(heatLayer);
        } catch (err) {
            console.error('Error cargando gas', tipo, err);
        }
    }

    /**
     * El backend devuelve { data: { 0:[...], 1:[...], ... } }
     * Cogemos la hora actual si existe; si no, la última disponible.
     */
    function extraerPuntosDeHoraActual(json) {
        if (!json || !json.data) return [];
        const horas = Object.keys(json.data).map(h => parseInt(h, 10));
        if (!horas.length) return [];

        const ahora = new Date().getHours();
        const horaElegida = horas.includes(ahora) ? ahora : Math.max(...horas);

        return json.data[horaElegida] || [];
    }

    /**
     * Carga puestos de bicicletas.
     * 如果后端暂时没有这个 API，可以先注释掉 BIKES_ENDPOINT / cargarBicis 调用。
     */
    const BIKES_ENDPOINT = '/api/v1/bicis/puestos';

    async function cargarBicis() {
        try {
            const resp = await fetch(BIKES_ENDPOINT);
            if (!resp.ok) throw new Error('Error HTTP ' + resp.status);
            const lista = await resp.json();

            if (!Array.isArray(lista)) return;

            lista.forEach(p => {
                const marker = L.marker([p.lat, p.lon]);
                const nombre = p.nombre || p.name || 'Puesto de bicicletas';
                marker.bindPopup(nombre);
                capaBicis.addLayer(marker);
            });
        } catch (err) {
            console.error('Error cargando puestos de bicicletas:', err);
        }
    }
});
