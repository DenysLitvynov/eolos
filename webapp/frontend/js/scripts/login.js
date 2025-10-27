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

    boton.addEventListener('click', async () => {
        const correo = correoInput.value;
        const contrasena = contrasenaInput.value;
        const logicaFake = new LoginFake();
        try {
            const resultado = await logicaFake.login(correo, contrasena);
            localStorage.setItem('token', resultado.token);
            mensaje.textContent = 'Login exitoso!';
            // Redirigir a dashboard o index
            window.location.href = '/';
        } catch (error) {
            mensaje.textContent = 'Error en login';
            console.error(error);
        }
    });
});

// ----------------------------------------------------------
