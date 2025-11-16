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
    const nombre = nombreInput.value.trim();
    const apellido = apellidoInput.value.trim();
    const correo = correoInput.value.trim();
    const targeta_id = targetaIdInput.value.trim();
    const contrasena = contrasenaInput.value;
    const contrasena_repite = contrasenaRepiteInput.value;
    const acepta_politica = document.getElementById('acepta_politica').checked;
       
    console.log("CHECKBOX VALUE:", acepta_politica);
    console.log("ENVIANDO AL BACKEND:", { nombre, apellido, correo, targeta_id, contrasena, contrasena_repite, acepta_politica });
    
    if (!acepta_politica) {
        mensaje.textContent = 'Debes aceptar la política de privacidad.';
        return;
    }

    // Validación frontend
    if (!nombre || !apellido || !correo || !targeta_id || !contrasena || !contrasena_repite) {
        mensaje.textContent = 'Completa todos los campos.';
        return;
    }
    if (contrasena !== contrasena_repite) {
        mensaje.textContent = 'Las contraseñas no coinciden.';
        return;
    }
    if (!acepta_politica) {
        mensaje.textContent = 'Debes aceptar la política de privacidad.';
        return;
    }

    const logicaRegistroFake = new RegistroFake();
    try {
        const resultadoRegistro = await logicaRegistroFake.registro(
            nombre, apellido, correo, targeta_id, contrasena, contrasena_repite, acepta_politica
        );
        mensaje.textContent = resultadoRegistro.mensaje;

        // Auto-login
        const logicaLoginFake = new LoginFake();
        const resultadoLogin = await logicaLoginFake.login(correo, contrasena);
        localStorage.setItem('token', resultadoLogin.token);
        mensaje.textContent = 'Registro e inicio de sesión exitosos! Redirigiendo...';
        setTimeout(() => { window.location.href = '/pages/prueba.html'; }, 2000);
    } catch (error) {
        mensaje.textContent = 'Error: ' + (error.message || 'Datos inválidos');
    }
    });
});

// ----------------------------------------------------------
