// frontend/js/scripts/perfil.js
// Prefijo base: el backend define prefix="/api/v1" en app.py
const API_BASE = '/api/v1';

const log = (...args) => console.log(new Date().toISOString(), '[perfil]', ...args);
const err = (...args) => console.error(new Date().toISOString(), '[perfil:ERR]', ...args);

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    log('token =', token);

    // Si no hay token → redirigir al login
    if (!token) {
        alert('No hay token, inicia sesión.');
        window.location.href = '/pages/login.html';
        return;
    }

    // ====== Obtener referencias de elementos del DOM ======
    const inputs = {
        nombre: document.getElementById('nombre'),
        correo: document.getElementById('correo'),
        targeta_id: document.getElementById('targeta_id'),
        contrasena_actual: document.getElementById('contrasena_actual'),
        nueva_contrasena: document.getElementById('nueva_contrasena'),
        repetir_contrasena: document.getElementById('repetir_contrasena')
    };

    const errors = {
        nombre: document.getElementById('nombreError'),
        correo: document.getElementById('correoError'),
        targeta_id: document.getElementById('targeta_idError'),
        contrasena_actual: document.getElementById('contrasena_actualError'),
        nueva_contrasena: document.getElementById('nueva_contrasenaError'),
        repetir_contrasena: document.getElementById('repetir_contrasenaError')
    };

    const mensaje = document.getElementById('mensajePerfil');
    const [$btnGuardar, $btnVolver] = document.querySelectorAll('.buttonperfil button');

    // ====== Botón de mostrar/ocultar contraseña ======
    document.addEventListener('click', (e) => {
        if (!e.target.classList.contains('toggle-password')) return;

        const wrapper = e.target.closest('.password-wrapper');
        const input = wrapper ? wrapper.querySelector('input[type="password"], input[type="text"]') : null;
        if (!input) return;

        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        e.target.textContent = isPassword ? 'Ocultar' : 'Mostrar';
    });

    // ====== Helpers de manejo de errores ======
    function mostrarError(elemento, mensaje) {
        if (!elemento) return;
        elemento.textContent = mensaje;
        elemento.classList.add('show');
    }

    function ocultarError(elemento) {
        if (!elemento) return;
        elemento.textContent = '';
        elemento.classList.remove('show');
    }

    // Validación individual por campo (al perder foco)
    function setupValidation(input, errorElement) {
        if (!input) return;
        input.addEventListener('blur', () => {
            if (!input.value.trim()) {
                mostrarError(errorElement, 'Este campo es obligatorio');
                input.classList.add('error');
            } else {
                ocultarError(errorElement);
                input.classList.remove('error');
            }
        });
    }

    setupValidation(inputs.nombre, errors.nombre);
    setupValidation(inputs.correo, errors.correo);
    // targeta_id es opcional → no requiere validación de obligatorio

    // ====== Validación de nueva contraseña: misma regla que en registro ======
    // Mínimo 8 caracteres, debe incluir: mayúscula, minúscula, número y símbolo (@$!%*?&)
    function validarContrasena(password) {
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;
        return regex.test(password);
    }

    // ====== Wrapper fetch con token Bearer ======
    const authFetch = async (path, options = {}) => {
        const url = `${API_BASE}${path}`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...(options.headers || {}),
        };
        const resp = await fetch(url, { ...options, headers });
        return resp;
    };

    // API GET y PUT perfil
    const apiGetPerfil = () => authFetch('/perfil', { method: 'GET' });
    const apiPutPerfil = (payload) =>
        authFetch('/perfil', { method: 'PUT', body: JSON.stringify(payload) });

    // ====== Cargar los datos del perfil desde el servidor ======
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
            log('perfil cargado:', user);

            // Rellenar inputs
            inputs.nombre.value = user.nombre ?? '';
            inputs.correo.value = user.correo ?? '';
            inputs.targeta_id.value = user.targeta_id ?? '';

            // Limpiar campos de contraseña
            inputs.contrasena_actual.value = '';
            inputs.nueva_contrasena.value = '';
            inputs.repetir_contrasena.value = '';

        } catch (e) {
            err('cargarPerfil()', e);
            alert('Error cargando el perfil');
        }
    };

    await cargarPerfil();

    // ====== Validar el formulario completo antes de enviar ======
    function validarFormulario() {
        let isValid = true;

        // 1) nombre / correo obligatorios
        ['nombre', 'correo'].forEach((key) => {
            const input = inputs[key];
            const errorEl = errors[key];
            if (!input.value.trim()) {
                mostrarError(errorEl, 'Este campo es obligatorio');
                input.classList.add('error');
                isValid = false;
            } else {
                ocultarError(errorEl);
                input.classList.remove('error');
            }
        });

        // 2) targeta_id opcional → sólo limpiar error
        ocultarError(errors.targeta_id);
        inputs.targeta_id.classList.remove('error');

        // 3) contraseña actual siempre obligatoria
        const actual = inputs.contrasena_actual.value.trim();
        if (!actual) {
            mostrarError(errors.contrasena_actual, 'Debes introducir tu contraseña actual');
            inputs.contrasena_actual.classList.add('error');
            isValid = false;
        } else {
            ocultarError(errors.contrasena_actual);
            inputs.contrasena_actual.classList.remove('error');
        }

        // 4) lógica nueva contraseña: solo si intenta cambiarla
        const nueva = inputs.nueva_contrasena.value;
        const repetir = inputs.repetir_contrasena.value;

        if (nueva || repetir) {
            // Si uno tiene contenido → ambos son obligatorios
            if (!nueva) {
                mostrarError(errors.nueva_contrasena, 'Introduce la nueva contraseña');
                inputs.nueva_contrasena.classList.add('error');
                isValid = false;
            }
            if (!repetir) {
                mostrarError(errors.repetir_contrasena, 'Debes repetir la nueva contraseña');
                inputs.repetir_contrasena.classList.add('error');
                isValid = false;
            }

            if (nueva && repetir) {
                if (nueva !== repetir) {
                    mostrarError(errors.repetir_contrasena, 'Las nuevas contraseñas no coinciden');
                    inputs.repetir_contrasena.classList.add('error');
                    isValid = false;
                } else if (!validarContrasena(nueva)) {
                    mostrarError(
                        errors.nueva_contrasena,
                        'La nueva contraseña no cumple los requisitos: mínimo 8 caracteres, con mayúsculas, minúsculas, números y símbolos (@$!%*?&)'
                    );
                    inputs.nueva_contrasena.classList.add('error');
                    isValid = false;
                } else {
                    ocultarError(errors.nueva_contrasena);
                    inputs.nueva_contrasena.classList.remove('error');
                }
            }
        } else {
            // Si no cambia contraseña → ambos campos pueden quedar vacíos
            ocultarError(errors.nueva_contrasena);
            ocultarError(errors.repetir_contrasena);
            inputs.nueva_contrasena.classList.remove('error');
            inputs.repetir_contrasena.classList.remove('error');
        }

        return isValid;
    }

    // ====== Guardar cambios perfil ======
    $btnGuardar.addEventListener('click', async () => {
        if (!validarFormulario()) {
            if (mensaje) {
                mensaje.textContent = 'Por favor, corrige los errores antes de guardar.';
                mensaje.style.color = '#d32f2f';
            } else {
                alert('Por favor, corrige los errores antes de guardar.');
            }
            return;
        }

        const actual = inputs.contrasena_actual.value.trim();
        const nueva  = inputs.nueva_contrasena.value.trim();

        const payload = {
            nombre: inputs.nombre.value.trim() || null,
            apellido: null,  // ya no se usa apellido en frontend → enviar null
            correo: inputs.correo.value.trim() || null,
            targeta_id: inputs.targeta_id.value.trim() || null,

            // Campos que coinciden con PerfilUpdateIn del backend
            contrasena_actual: actual,           // obligatorio
            contrasena_nueva: nueva || null      // opcional
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

                console.error(`Error ${resp.status} desde el backend:`, data);

                let msg = 'Error actualizando perfil';
                if (Array.isArray(data?.detail)) {
                    msg = data.detail
                        .map(err => `${err.loc?.join('.')}: ${err.msg}`)
                        .join(' | ');
                } else if (typeof data?.detail === 'string') {
                    msg = data.detail;
                }

                throw new Error(msg);
            }

            // Actualizar valores visibles
            inputs.nombre.value = data.nombre ?? '';
            inputs.correo.value = data.correo ?? '';
            inputs.targeta_id.value = data.targeta_id ?? '';

            // Limpiar campos contraseña
            inputs.contrasena_actual.value = '';
            inputs.nueva_contrasena.value = '';
            inputs.repetir_contrasena.value = '';

            if (mensaje) {
                mensaje.textContent = 'Perfil actualizado correctamente.';
                mensaje.style.color = 'green';
            } else {
                alert('Perfil actualizado correctamente');
            }

            log('perfil actualizado');
        } catch (e) {
            err('PUT /perfil', e);
            if (mensaje) {
                mensaje.textContent = e.message || 'Error actualizando perfil';
                mensaje.style.color = '#d32f2f';
            } else {
                alert(e.message || 'Error actualizando perfil');
            }
        }
    });

    // ====== Regresar al inicio ======
    $btnVolver.addEventListener('click', () => {
        window.location.href = '/';
    });
});
