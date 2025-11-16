/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para registro.html. Solo validaciones básicas de frontend.
*/

import { RegistroFake } from '../logica_fake/registro_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const registroFake = new RegistroFake();
    const boton = document.getElementById('registroBtn');
    const mensaje = document.getElementById('mensaje');

    const inputs = {
        nombre: document.getElementById('nombre'),
        apellido: document.getElementById('apellido'),
        correo: document.getElementById('correo'),
        targeta_id: document.getElementById('targeta_id'),
        contrasena: document.getElementById('contrasena'),
        contrasena_repite: document.getElementById('contrasena_repite'),
        acepta_politica: document.getElementById('acepta_politica')
    };

    const errors = {
        nombre: document.getElementById('nombreError'),
        apellido: document.getElementById('apellidoError'),
        correo: document.getElementById('correoError'),
        targeta_id: document.getElementById('targeta_idError'),
        contrasena: document.getElementById('contrasenaError'),
        contrasena_repite: document.getElementById('contrasena_repiteError'),
        acepta_politica: document.getElementById('acepta_politicaError')
    };

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
            if (!input.value.trim()) {
                mostrarError(errorElement, 'Este campo es obligatorio');
                input.classList.add('error');
            } else {
                ocultarError(errorElement);
                input.classList.remove('error');
            }
        });
    }

    // Configurar validaciones para campos básicos
    setupValidation(inputs.nombre, errors.nombre);
    setupValidation(inputs.apellido, errors.apellido);
    setupValidation(inputs.correo, errors.correo);
    setupValidation(inputs.targeta_id, errors.targeta_id);
    setupValidation(inputs.contrasena, errors.contrasena);

    // Validación especial para repetir contraseña
    inputs.contrasena_repite.addEventListener('blur', () => {
        const valor = inputs.contrasena_repite.value;
        const contrasena = inputs.contrasena.value;
        if (!valor) {
            mostrarError(errors.contrasena_repite, 'Debes repetir la contraseña');
            inputs.contrasena_repite.classList.add('error');
        } else if (valor !== contrasena) {
            mostrarError(errors.contrasena_repite, 'Las contraseñas no coinciden');
            inputs.contrasena_repite.classList.add('error');
        } else {
            ocultarError(errors.contrasena_repite);
            inputs.contrasena_repite.classList.remove('error');
        }
    });

    // Validación del checkbox
    inputs.acepta_politica.addEventListener('change', () => {
        if (!inputs.acepta_politica.checked) {
            mostrarError(errors.acepta_politica, 'Debes aceptar la política de privacidad y términos');
        } else {
            ocultarError(errors.acepta_politica);
        }
    });

    function validarFormulario() {
        let isValid = true;

        // Verificar campos obligatorios
        if (!inputs.nombre.value.trim()) {
            mostrarError(errors.nombre, 'El nombre es obligatorio');
            inputs.nombre.classList.add('error');
            isValid = false;
        }
        if (!inputs.apellido.value.trim()) {
            mostrarError(errors.apellido, 'El apellido es obligatorio');
            inputs.apellido.classList.add('error');
            isValid = false;
        }
        if (!inputs.correo.value.trim()) {
            mostrarError(errors.correo, 'El correo electrónico es obligatorio');
            inputs.correo.classList.add('error');
            isValid = false;
        }
        if (!inputs.targeta_id.value.trim()) {
            mostrarError(errors.targeta_id, 'El ID de tarjeta es obligatorio');
            inputs.targeta_id.classList.add('error');
            isValid = false;
        }
        if (!inputs.contrasena.value) {
            mostrarError(errors.contrasena, 'La contraseña es obligatoria');
            inputs.contrasena.classList.add('error');
            isValid = false;
        }
        if (!inputs.contrasena_repite.value) {
            mostrarError(errors.contrasena_repite, 'Debes repetir la contraseña');
            inputs.contrasena_repite.classList.add('error');
            isValid = false;
        } else if (inputs.contrasena_repite.value !== inputs.contrasena.value) {
            mostrarError(errors.contrasena_repite, 'Las contraseñas no coinciden');
            inputs.contrasena_repite.classList.add('error');
            isValid = false;
        }
        if (!inputs.acepta_politica.checked) {
            mostrarError(errors.acepta_politica, 'Debes aceptar la política de privacidad y términos');
            isValid = false;
        }

        return isValid;
    }

    boton.addEventListener('click', async () => {
        // Validación básica antes de enviar
        if (!validarFormulario()) {
            mensaje.textContent = 'Por favor, completa todos los campos obligatorios y corrige los errores';
            mensaje.style.color = '#d32f2f';
            return;
        }

        const data = {
            nombre: inputs.nombre.value.trim(),
            apellido: inputs.apellido.value.trim(),
            correo: inputs.correo.value.trim(),
            targeta_id: inputs.targeta_id.value.trim(),
            contrasena: inputs.contrasena.value,
            contrasena_repite: inputs.contrasena_repite.value,
            acepta_politica: inputs.acepta_politica.checked
        };

        try {
            mensaje.textContent = 'Procesando registro...';
            mensaje.style.color = '#666';

            await registroFake.registro(
                data.nombre,
                data.apellido,
                data.correo,
                data.targeta_id,
                data.contrasena,
                data.contrasena_repite,
                data.acepta_politica
            );

            // GUARDAR EMAIL PARA VERIFICACIÓN
            localStorage.setItem('pending_email', data.correo);

            mensaje.textContent = '¡Registro exitoso! Código de verificación enviado. Redirigiendo...';
            mensaje.style.color = 'green';

            setTimeout(() => {
                window.location.href = '/pages/verify-registration.html';
            }, 2000);

        } catch (error) {
            // MENSAJES ESPECÍFICOS PARA CONTRASEÑA
            const mensajeError = error.message || '';
            
            if (mensajeError.includes('contraseña') && mensajeError.includes('mínimo 8')) {
                mensaje.textContent = 'La contraseña no cumple los requisitos: debe tener mínimo 8 caracteres, incluir mayúsculas, minúsculas, números y símbolos (@$!%*?&)';
            } else if (mensajeError.includes('ID de carnet no existe')) {
                mensaje.textContent = 'El ID de carnet no existe en nuestro sistema';
            } else if (mensajeError.includes('ya registrado')) {
                mensaje.textContent = 'Este correo o carnet ya está registrado';
            } else if (mensajeError.includes('política')) {
                mensaje.textContent = 'Debes aceptar la política de privacidad y términos';
            } else {
                mensaje.textContent = 'Error en el registro. Verifica que todos los datos sean correctos.';
            }
            
            mensaje.style.color = '#d32f2f';
            console.error('Error detallado en registro:', error);
        }
    });

    // Permitir envío con Enter
    Object.values(inputs).forEach(input => {
        if (input.type !== 'checkbox') {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    boton.click();
                }
            });
        }
    });
});
