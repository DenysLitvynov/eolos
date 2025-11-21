/* 
Autor: Denys Litvynov Lymanets
Fecha: 26-10-2025
Descripción: Handlers para login.html.
*/

import { LoginFake } from '../logica_fake/login_fake.js';

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
            localStorage.setItem('token', resultado.token);
            mensaje.textContent = '¡Login exitoso! Redirigiendo...';
            mensaje.style.color = 'green';
            
            // Redirigir a la página de prueba
            setTimeout(() => { 
                window.location.href = '/pages/prueba.html'; 
            }, 1500);
            
        } catch (error) {
            // MENSAJE ESPECÍFICO PARA LOGIN
            const mensajeError = error.message || '';
            
            if (mensajeError.includes('Credenciales inválidas')) {
                mensaje.textContent = 'Correo electrónico o contraseña incorrectos. Verifica tus credenciales.';
            } else if (mensajeError.includes('contraseña') && mensajeError.includes('mínimo 8')) {
                mensaje.textContent = 'La contraseña no cumple los requisitos de seguridad';
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
