/* 
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Handlers para login.html.
*/

import { LoginFake } from '../logica_fake/login_fake.js';

// ----------------------------------------------------------

// Función para decodificar JWT sin librerías externas
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

// ----------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('loginBtn');
    const mensaje = document.getElementById('mensaje');
    const correoInput = document.getElementById('correo');
    const contrasenaInput = document.getElementById('contrasena');
    const correoError = document.getElementById('correoError');
    const contrasenaError = document.getElementById('contrasenaError');

    // CORRECCIÓN: Botón ojo para contraseña - Event delegation
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('toggle-password')) {
            e.preventDefault();
            const wrapper = e.target.closest('.password-wrapper');
            const input = wrapper.querySelector('input');
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                e.target.textContent = isPassword ? 'Ocultar' : 'Mostrar';
            }
        }
    });

    // Validación básica en tiempo real
    correoInput.addEventListener('input', () => {
        const correo = correoInput.value.trim();
        if (!correo) {
            mostrarError(correoError, 'El correo electrónico es obligatorio');
            correoInput.classList.add('error');
        } else {
            ocultarError(correoError);
            correoInput.classList.remove('error');
        }
    });

    contrasenaInput.addEventListener('input', () => {
        const contrasena = contrasenaInput.value;
        if (!contrasena) {
            mostrarError(contrasenaError, 'La contraseña es obligatoria');
            contrasenaInput.classList.add('error');
        } else {
            ocultarError(contrasenaError);
            contrasenaInput.classList.remove('error');
        }
    });

    function mostrarError(elemento, mensaje) {
        elemento.textContent = mensaje;
        elemento.classList.add('show');
    }

    function ocultarError(elemento) {
        elemento.textContent = '';
        elemento.classList.remove('show');
    }

    function validarFormulario() {
        let isValid = true;
        const correo = correoInput.value.trim();
        const contrasena = contrasenaInput.value;

        // Validaciones básicas de frontend
        if (!correo) {
            mostrarError(correoError, 'El correo electrónico es obligatorio');
            correoInput.classList.add('error');
            isValid = false;
        }

        if (!contrasena) {
            mostrarError(contrasenaError, 'La contraseña es obligatoria');
            contrasenaInput.classList.add('error');
            isValid = false;
        }

        return isValid;
    }

    boton.addEventListener('click', async () => {
        // Validación básica antes de enviar
        if (!validarFormulario()) {
            mensaje.textContent = 'Por favor, completa todos los campos obligatorios';
            mensaje.style.color = '#d32f2f';
            return;
        }

        const correo = correoInput.value.trim();
        const contrasena = contrasenaInput.value;

        const logicaFake = new LoginFake();
        try {
            mensaje.textContent = 'Iniciando sesión...';
            mensaje.style.color = '#666';
            
            const resultado = await logicaFake.login(correo, contrasena);
            
            if (!resultado || !resultado.token) {
                throw new Error('No se recibió token del servidor');
            }
            
            localStorage.setItem('token', resultado.token);
            
            // DEBUG: Mostrar el token en consola para verificar
            console.log('Token recibido:', resultado.token);
            
            // Decodificar el token para obtener los roles
            const decoded = parseJwt(resultado.token);
            console.log('Token decodificado:', decoded); // DEBUG
            
            if (!decoded) {
                throw new Error('Token inválido');
            }
            
            const roles = decoded.roles; // Array de roles, e.g., ["usuario", "admin"]
            console.log('Roles del usuario:', roles); // DEBUG
            
            if (!roles || !Array.isArray(roles) || roles.length === 0) {
                throw new Error('El usuario no tiene roles asignados');
            }
            
            let redirectUrl = '/index.html'; // Default para usuario estándar
            
            // Lógica de redirección basada en roles
            if (roles.includes('admin')) {
                redirectUrl = '/pages/tecnico/estado-sensores.html';
                console.log('Redirigiendo a estado-sensores.html (admin)');
            } else if (roles.includes('tecnico')) {
                redirectUrl = '/pages/tecnico/estado-sensores.html'; 
                console.log('Redirigiendo a estado-sensores.html (tecnico)');
            } else if (roles.includes('usuario')) {
                redirectUrl = '/index.html'; 
                console.log('Redirigiendo a index.html (usuario)');
            } else {
                console.log('Rol no reconocido, redirigiendo por defecto');
            }
            
            mensaje.textContent = '¡Login exitoso! Redirigiendo...';
            mensaje.style.color = 'green';
            
            // Redirigir a la página correspondiente
            setTimeout(() => { 
                console.log('Redirigiendo a:', redirectUrl);
                window.location.href = redirectUrl; 
            }, 1500);
            
        } catch (error) {
            // MENSAJE ESPECÍFICO PARA LOGIN
            const mensajeError = error.message || '';
            
            if (mensajeError.includes('Credenciales inválidas')) {
                mensaje.textContent = 'Correo electrónico o contraseña incorrectos. Verifica tus credenciales.';
            } else if (mensajeError.includes('No se recibió token') || 
                       mensajeError.includes('Token inválido') ||
                       mensajeError.includes('no tiene roles')) {
                mensaje.textContent = 'Error en la autenticación. Contacta al administrador.';
                console.error('Error de autenticación:', error);
            } else {
                mensaje.textContent = 'Error al iniciar sesión. Verifica tus credenciales.';
            }
            
            mensaje.style.color = '#d32f2f';
            console.error('Error en login:', error);
        }
    });

    // Permitir login con Enter
    [correoInput, contrasenaInput].forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                boton.click();
            }
        });
    });
});

// ----------------------------------------------------------
