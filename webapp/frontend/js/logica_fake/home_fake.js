class HomeFake {
    constructor(prefix = "home_") { this.prefix = prefix; }
    _k(uid) { return `${this.prefix}${uid}`; }
    _delay(ms = 80) { return new Promise(r => setTimeout(r, ms)); }

    async ensureSeed(uid) {
        await this._delay();
        const k = this._k(uid);
        if (!localStorage.getItem(k)) {
            localStorage.setItem(k, JSON.stringify({
                usuario: { usuario_id: uid, nombre_visible: "Usuario Fake" },
                placa_id: "fake-placa",
                calidad_aire: { score: 46, estado: "Buena", descripcion: "..." },
                nivel_actual: { gases: [
                        { tipo: "pm2_5", valor: 12.3, unidad: "µg/m³" },
                        { tipo: "no2", valor: 80.1, unidad: "µg/m³" },
                        { tipo: "co", valor: 1.4, unidad: "mg/m³" },
                        { tipo: "temperatura", valor: 22.7, unidad: "°C" },
                    ]},
                impacto: { rutas_limpias: 2, co2_kg: 0.2, puntos: 10 },
                ultimo_trayecto: { distancia_km: 2.8, tiempo_min: 21, calidad_promedio: "Buena" }
            }));
        }
    }

    async getHome(uid) {
        await this._delay();
        const raw = localStorage.getItem(this._k(uid));
        return raw ? JSON.parse(raw) : null;
    }
}
window.HomeFake = HomeFake;
