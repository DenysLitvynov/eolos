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
    const toggles = document.querySelectorAll('.toggle-password');

    if (!token) {
        mensaje.textContent = 'Enlace inválido.';
        resetBtn.disabled = true;
        return;
    }

    toggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            input.type = input.type === 'password' ? 'text' : 'password';
            toggle.textContent = input.type === 'password' ? 'Mostrar' : 'Ocultar';
        });
    });

    resetBtn.addEventListener('click', async () => {
        const contrasena = contrasenaInput.value;
        const contrasena_repite = repiteInput.value;

        if (contrasena !== contrasena_repite) {
            mensaje.textContent = 'Las contraseñas no coinciden.';
            return;
        }
        if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(contrasena)) {
            mensaje.textContent = 'Contraseña débil: mínimo 8 caracteres, mayús, minús, número y símbolo.';
            return;
        }

        try {
            await fake.resetear(token, contrasena, contrasena_repite);
            mensaje.textContent = '¡Contraseña cambiada! Redirigiendo...';
            mensaje.style.color = 'green';
            setTimeout(() => { window.location.href = '/pages/login.html'; }, 2000);
        } catch (error) {
            mensaje.textContent = 'Enlace inválido o expirado.';
        }
    });
});
