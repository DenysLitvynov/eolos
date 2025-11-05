// frontend/js/scripts/perfil.js
// Prefijo unificado: el backend usa prefix="/api/v1" en app.py
const API_BASE = '/api/v1';

const log = (...args) => console.log(new Date().toISOString(), '[perfil]', ...args);
const err = (...args) => console.error(new Date().toISOString(), '[perfil:ERR]', ...args);

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    log('token =', token);

    // ====== Vincular elementos del DOM ======
    const $nombre = document.getElementById('nombre');
    const $correo = document.getElementById('correo');
    const $targeta = document.getElementById('targeta_id'); // Nota: el nombre del campo es exactamente targeta_id
    const $contrasena = document.getElementById('contrasena');
    const $fecha = document.getElementById('fecha'); // Se usa para mostrar fecha_registro (solo lectura)

    const [$btnGuardar, $btnVolver] = document.querySelectorAll('.buttonperfil button');

    // ====== Fetch genérico (siempre con Bearer; nunca concatenar ?usuario_id=guest) ======
    const authFetch = async (path, options = {}) => {
        if (!token) {
            throw new Error('No hay token almacenado');
        }
        const url = `${API_BASE}${path}`;         // Solo concatenar /api/v1 + ruta
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,     // Siempre incluir Authorization
            ...(options.headers || {}),
        };
        const resp = await fetch(url, { ...options, headers });
        return resp;
    };

    // ====== Envoltorios de API ======
    const apiGetPerfil = () => authFetch('/perfil', { method: 'GET' });
    const apiPutPerfil = (payload) =>
        authFetch('/perfil', { method: 'PUT', body: JSON.stringify(payload) });

    // ====== Sin token -> redirigir al login ======
    if (!token) {
        alert('No hay token, inicia sesión.');
        window.location.href = '/pages/login.html';
        return;
    }

    // ====== Cargar datos del perfil ======
    const cargarPerfil = async () => {
        try {
            const resp = await apiGetPerfil();
            if (!resp.ok) {
                const text = await resp.text();
                err('❌ GET FAIL', resp.status, text);
                if (resp.status === 401) {
                    localStorage.removeItem('token');
                    alert('Sesión expirada o inválida. Inicia sesión de nuevo.');
                    window.location.href = '/pages/login.html';
                    return;
                }
                throw new Error('No se pudo cargar el perfil');
            }
            const user = await resp.json();

            // Rellenar el formulario
            $nombre.value = user.nombre ?? '';
            $correo.value = user.correo ?? '';
            $targeta.value = user.targeta_id ?? '';

            // Mostrar fecha_registro (solo lectura)
            $fecha.value = user.fecha_registro ?? '';
            $fecha.readOnly = true;
            $fecha.disabled = true;
            $fecha.title = 'Solo lectura';
            log('perfil cargado');
        } catch (e) {
            err('cargarPerfil()', e);
            alert('Error cargando el perfil');
        }
    };

    // Cargar una vez al inicio
    await cargarPerfil();

    // ====== Guardar cambios del perfil ======
    $btnGuardar.addEventListener('click', async () => {
        const payload = {
            nombre: $nombre.value.trim() || null,
            correo: $correo.value.trim() || null,
            targeta_id: $targeta.value.trim() || null,
            contrasena: $contrasena.value.trim() ? $contrasena.value : null, // Si está vacío, no cambia la contraseña
            // No enviar fecha_registro (solo lectura), ni rol_id/usuario_id (el backend los obtiene del token)
        };

        try {
            const resp = await apiPutPerfil(payload);
            const data = await resp.json().catch(() => ({}));
            if (!resp.ok) {
                if (resp.status === 401) {
                    localStorage.removeItem('token');
                    alert('Sesión expirada o inválida. Inicia sesión de nuevo.');
                    window.location.href = '/pages/login.html';
                    return;
                }
                const msg = data?.detail || 'Error actualizando perfil';
                throw new Error(msg);
            }

            // Actualizar formulario con los datos devueltos
            $nombre.value = data.nombre ?? '';
            $correo.value = data.correo ?? '';
            $targeta.value = data.targeta_id ?? '';
            $fecha.value = data.fecha_registro ?? '';

            // Limpiar el campo de contraseña
            $contrasena.value = '';
            alert('Perfil actualizado correctamente');
            log('perfil actualizado');
        } catch (e) {
            err('PUT /perfil', e);
            alert(e.message || 'Error actualizando perfil');
        }
    });

    // ====== Volver al inicio ======
    $btnVolver.addEventListener('click', () => {
        window.location.href = '/';
    });
});
