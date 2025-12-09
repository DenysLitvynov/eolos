// js/logica_fake/admin-fake.js
// Autor: jinwei
// Fecha: 07-12-2025
// Descripción: Simulación de la API de admin (usuarios) sólo en frontend.

(function () {
    const STORAGE_KEY = "admin_fake_usuarios";

    function loadFromStorage() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (e) {
            console.warn("Error leyendo usuarios fake de localStorage", e);
            return null;
        }
    }

    function saveToStorage(list) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
        } catch (e) {
            console.warn("Error guardando usuarios fake en localStorage", e);
        }
    }

    function defaultUsers() {
        return [
            {
                usuario_id: "11111111-1111-1111-1111-111111111111",
                targeta_id: "2025-03-27T14:05:03+0000",
                nombre: "María",
                apellido: "Fernández",
                rol: "tecnico",
                correo: "maria@demo.com",
            },
            {
                usuario_id: "22222222-2222-2222-2222-222222222222",
                targeta_id: "2025-03-27T14:05:03+0000",
                nombre: "Juan",
                apellido: "Bautista",
                rol: "admin",
                correo: "admin@demo.com",
            },
        ];
    }

    function ensureData() {
        let list = loadFromStorage();
        if (!list || !Array.isArray(list) || list.length === 0) {
            list = defaultUsers();
            saveToStorage(list);
        }
        return list;
    }

    function generateId() {
        if (window.crypto && window.crypto.randomUUID) {
            return window.crypto.randomUUID();
        }
        return "fake-" + Math.random().toString(16).slice(2, 10);
    }

    const AdminApiFake = {
        async listarUsuarios() {
            return ensureData();
        },

        async crearUsuario(payload) {
            const list = ensureData();
            const nuevo = {
                usuario_id: generateId(),
                targeta_id: payload.targeta_id || null,
                nombre: payload.nombre || "",
                apellido: payload.apellido || "",
                rol: payload.rol || "usuario",
                correo: payload.correo || "",
            };
            list.push(nuevo);
            saveToStorage(list);
            return nuevo;
        },

        async actualizarUsuario(usuario_id, payload) {
            const list = ensureData();
            const idx = list.findIndex((u) => u.usuario_id === usuario_id);
            if (idx === -1) throw new Error("Usuario no encontrado (fake)");

            const usuario = list[idx];
            const actualizado = {
                ...usuario,
                ...payload,
            };
            list[idx] = actualizado;
            saveToStorage(list);
            return actualizado;
        },

        async eliminarUsuario(usuario_id) {
            const list = ensureData();
            const idx = list.findIndex((u) => u.usuario_id === usuario_id);
            if (idx === -1) throw new Error("Usuario no encontrado (fake)");
            list.splice(idx, 1);
            saveToStorage(list);
            return true;
        },
    };

    window.AdminApiFake = AdminApiFake;
})();
