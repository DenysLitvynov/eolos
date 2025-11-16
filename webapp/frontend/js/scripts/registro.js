/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para registro.html. Solo interfaz.
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

    // Botón ojo
    document.querySelectorAll('.toggle-password').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            input.type = input.type === 'password' ? 'text' : 'password';
            toggle.textContent = input.type === 'password' ? 'Mostrar' : 'Ocultar';
        });
    });

    boton.addEventListener('click', async () => {
        const data = {
            nombre: inputs.nombre.value.trim(),
            apellido: inputs.apellido.value.trim(),
            correo: inputs.correo.value.trim(),
            targeta_id: inputs.targeta_id.value.trim(),
            contrasena: inputs.contrasena.value,
            contrasena_repite: inputs.contrasena_repite.value,
            acepta_politica: inputs.acepta_politica.checked
        };

        // Validaciones frontend
        if (!data.acepta_politica) {
            mensaje.textContent = 'Debes aceptar la política de privacidad.';
            return;
        }
        if (!data.nombre || !data.apellido || !data.correo || !data.targeta_id || !data.contrasena) {
            mensaje.textContent = 'Completa todos los campos.';
            return;
        }
        if (data.contrasena !== data.contrasena_repite) {
            mensaje.textContent = 'Las contraseñas no coinciden.';
            return;
        }
        if (!/^\d{8}[A-Z]$/.test(data.targeta_id)) {
            mensaje.textContent = 'ID de carnet: 8 dígitos + 1 letra mayúscula.';
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.correo)) {
            mensaje.textContent = 'Correo inválido.';
            return;
        }
        if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(data.contrasena)) {
            mensaje.textContent = 'Contraseña débil: mínimo 8 caracteres, mayús, minús, número y símbolo.';
            return;
        }

        try {
            // SOLO REGISTRO (NO LOGIN)
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

            mensaje.textContent = 'Código enviado. Redirigiendo...';
            mensaje.style.color = 'green';

            setTimeout(() => {
                window.location.href = '/pages/verify-registration.html';
            }, 1500);

        } catch (error) {
            const err = error.message || '';
            if (err.includes('ID de carnet no existe')) {
                mensaje.textContent = 'ID de carnet no encontrado en el sistema.';
            } else if (err.includes('ya registrado')) {
                mensaje.textContent = 'Este correo o carnet ya está en uso.';
            } else {
                mensaje.textContent = 'Error en el registro. Inténtalo de nuevo.';
            }
            console.error('Error registro:', error);
        }
    });
});
