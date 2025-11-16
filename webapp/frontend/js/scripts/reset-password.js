/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para reset-password.html. Solo interfaz.
*/

import { ResetPasswordFake } from '../logica_fake/reset_password_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const fake = new ResetPasswordFake();
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const contrasenaInput = document.getElementById('contrasena');
    const repiteInput = document.getElementById('contrasena_repite');
    const resetBtn = document.getElementById('resetBtn');
    const mensaje = document.getElementById('mensaje');
    const contrasenaError = document.getElementById('contrasenaError');
    const repiteError = document.getElementById('contrasena_repiteError');

    if (!token) {
        mensaje.textContent = 'Enlace inválido o expirado. Solicita un nuevo enlace de recuperación.';
        mensaje.style.color = '#d32f2f';
        resetBtn.disabled = true;
        return;
    }

    // CORRECCIÓN: Botones ojo para contraseñas - Event delegation
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('toggle-password')) {
            e.preventDefault();
            const wrapper = e.target.closest('.password-wrapper');
            const input = wrapper.querySelector('input[type="password"], input[type="text"]');
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                e.target.textContent = isPassword ? 'Ocultar' : 'Mostrar';
            }
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

    // Validaciones básicas en tiempo real
    function setupValidation(input, errorElement) {
        input.addEventListener('blur', () => {
            if (!input.value) {
                mostrarError(errorElement, 'Este campo es obligatorio');
                input.classList.add('error');
            } else {
                ocultarError(errorElement);
                input.classList.remove('error');
            }
        });
    }

    setupValidation(contrasenaInput, contrasenaError);
    setupValidation(repiteInput, repiteError);

    // Validación especial para repetir contraseña
    repiteInput.addEventListener('blur', () => {
        const valor = repiteInput.value;
        const contrasena = contrasenaInput.value;
        if (valor && valor !== contrasena) {
            mostrarError(repiteError, 'Las contraseñas no coinciden');
            repiteInput.classList.add('error');
        }
    });

    function validarFormulario() {
        let isValid = true;

        if (!contrasenaInput.value) {
            mostrarError(contrasenaError, 'La contraseña es obligatoria');
            contrasenaInput.classList.add('error');
            isValid = false;
        }

        if (!repiteInput.value) {
            mostrarError(repiteError, 'Debes repetir la contraseña');
            repiteInput.classList.add('error');
            isValid = false;
        } else if (repiteInput.value !== contrasenaInput.value) {
            mostrarError(repiteError, 'Las contraseñas no coinciden');
            repiteInput.classList.add('error');
            isValid = false;
        }

        return isValid;
    }

    resetBtn.addEventListener('click', async () => {
        if (!validarFormulario()) {
            mensaje.textContent = 'Por favor, completa todos los campos y corrige los errores';
            mensaje.style.color = '#d32f2f';
            return;
        }

        const contrasena = contrasenaInput.value;
        const contrasena_repite = repiteInput.value;

        try {
            mensaje.textContent = 'Estableciendo nueva contraseña...';
            mensaje.style.color = '#666';

            await fake.resetear(token, contrasena, contrasena_repite);
            
            mensaje.textContent = '¡Contraseña cambiada exitosamente! Redirigiendo al login...';
            mensaje.style.color = 'green';
            
            setTimeout(() => { 
                window.location.href = '/pages/login.html'; 
            }, 2000);
            
        } catch (error) {
            // MENSAJES ESPECÍFICOS PARA CONTRASEÑA
            const mensajeError = error.message || '';
            
            if (mensajeError.includes('contraseña') && mensajeError.includes('mínimo 8')) {
                mensaje.textContent = 'La contraseña no cumple los requisitos de seguridad: debe tener mínimo 8 caracteres, incluir mayúsculas, minúsculas, números y símbolos (@$!%*?&)';
            } else if (mensajeError.includes('Token inválido') || mensajeError.includes('Token expirado')) {
                mensaje.textContent = 'El enlace de recuperación ha expirado o es inválido. Solicita uno nuevo.';
            } else if (mensajeError.includes('Token ya usado')) {
                mensaje.textContent = 'Este enlace de recuperación ya ha sido utilizado. Solicita uno nuevo.';
            } else {
                mensaje.textContent = 'No se pudo completar el cambio de contraseña. Verifica que la contraseña cumpla con todos los requisitos.';
            }
            
            mensaje.style.color = '#d32f2f';
            console.error('Error detallado en reset password:', error);
        }
    });

    // Permitir envío con Enter
    [contrasenaInput, repiteInput].forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                resetBtn.click();
            }
        });
    });
});
