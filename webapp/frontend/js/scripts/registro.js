/* 
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Handlers para registro.html.
*/

import { RegistroFake } from '../logica_fake/registro_fake.js';  
import { LoginFake } from '../logica_fake/login_fake.js';  

// ----------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('registroBtn');
    const mensaje = document.getElementById('mensaje');
    const nombreInput = document.getElementById('nombre');
    const apellidoInput = document.getElementById('apellido');
    const correoInput = document.getElementById('correo');
    const targetaIdInput = document.getElementById('targeta_id');
    const contrasenaInput = document.getElementById('contrasena');
    const contrasenaRepiteInput = document.getElementById('contrasena_repite');

    boton.addEventListener('click', async () => {
        const nombre = nombreInput.value;
        const apellido = apellidoInput.value;
        const correo = correoInput.value;
        const targeta_id = targetaIdInput.value;
        const contrasena = contrasenaInput.value;
        const contrasena_repite = contrasenaRepiteInput.value;

        // Validación básica frontend 
        if (!nombre || !apellido || !correo || !targeta_id || !contrasena || !contrasena_repite) {
            mensaje.textContent = 'Por favor, completa todos los campos.';
            return;
        }
        if (contrasena !== contrasena_repite) {
            mensaje.textContent = 'Las contraseñas no coinciden.';
            return;
        }

        const logicaRegistroFake = new RegistroFake();
        try {
            const resultadoRegistro = await logicaRegistroFake.registro(nombre, apellido, correo, targeta_id, contrasena, contrasena_repite);
            mensaje.textContent = resultadoRegistro.mensaje;  // Muestra "Registro exitoso"

            // Auto-login inmediato
            const logicaLoginFake = new LoginFake();
            const resultadoLogin = await logicaLoginFake.login(correo, contrasena);
            localStorage.setItem('token', resultadoLogin.token);  // Almacena token como en login
            mensaje.textContent = 'Registro e inicio de sesión exitosos! Redirigiendo...';

            // Redirigir a prueba después de 2 segundos
            window.setTimeout(() => { window.location.href = '/pages/prueba.html'; }, 2000);
        } catch (error) {
            mensaje.textContent = 'Error en registro: ' + (error.message || 'Desconocido');
            console.error(error);
        }
    });
});

// ----------------------------------------------------------
