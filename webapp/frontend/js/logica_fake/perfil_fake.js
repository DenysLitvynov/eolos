// Perfil fake usando localStorage como "base de datos" local.
// API async para simular llamadas a servidor (fácil de reemplazar por fetch cuando tengas backend real).

class PerfilFake {
    constructor(storageKeyPrefix = 'perfil_') {
        this.prefix = storageKeyPrefix;
        // Puedes inicializar perfiles de ejemplo si quieres:
        this._initSampleDataIfMissing();
    }

    _storageKey(usuario_id) {
        return `${this.prefix}${usuario_id}`;
    }

    _initSampleDataIfMissing() {
        // Si no existe ningún perfil, crea uno de ejemplo para 'guest'
        const uid = localStorage.getItem('usuario_id') || 'guest';
        const key = this._storageKey(uid);
        if (!localStorage.getItem(key)) {
            const sample = {
                usuario_id: uid,
                nombre: 'Juan Pérez',
                correo: 'juanba@gmail.com',
                targeta_id: '12345HDC',
                // contrasena: solo si desea cambiarla, por seguridad no rellenamos
                fecha: '1990-01-01' // formato YYYY-MM-DD
            };
            localStorage.setItem(key, JSON.stringify(sample));
        }
    }

    // Simula latencia opcional (ms)
    _delay(ms = 150) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Obtener perfil por usuario_id (simula GET)
    async obtenerPerfil(usuario_id) {
        await this._delay();
        if (usuario_id == null) throw new Error('usuario_id es requerido');
        const key = this._storageKey(usuario_id);
        const raw = localStorage.getItem(key);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch (e) {
            console.warn('perfil_fake: JSON parse error', e);
            return null;
        }
    }

    // Actualizar perfil (simula PUT). datosPerfil puede incluir nombre, correo, targeta_id, contrasena, fecha
    async actualizarPerfil(usuario_id, datosPerfil) {
        await this._delay();
        if (usuario_id == null) throw new Error('usuario_id es requerido');

        const key = this._storageKey(usuario_id);
        const raw = localStorage.getItem(key);
        const existing = raw ? JSON.parse(raw) : { usuario_id };

        // Nota: en un backend real deberías hashear la contraseña y validar unicidad del correo, etc.
        // Aquí simplemente actualizamos las propiedades permitidas.
        const allowed = ['nombre', 'correo', 'targeta_id', 'contrasena', 'fecha'];
        for (const k of allowed) {
            if (k in datosPerfil) {
                // no guardamos contrasena si viene vacía
                if (k === 'contrasena' && (datosPerfil[k] === null || datosPerfil[k] === '')) {
                    continue;
                }
                existing[k] = datosPerfil[k];
            }
        }

        localStorage.setItem(key, JSON.stringify(existing));
        return existing;
    }

    // Borrar perfil (opcional)
    async borrarPerfil(usuario_id) {
        await this._delay();
        const key = this._storageKey(usuario_id);
        localStorage.removeItem(key);
        return true;
    }
}

// Exponer en window para uso desde otros scripts
window.PerfilFake = PerfilFake;
