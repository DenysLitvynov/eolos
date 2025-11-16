/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para forgot-password.html.
*/

import { PeticionarioREST } from '../utilidades/peticionario_REST.js';

document.addEventListener('DOMContentLoaded', () => {
    const peticionario = new PeticionarioREST();
    const correoInput = document.getElementById('correo');
    const sendBtn = document.getElementById('sendBtn');
    const resendBtn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');
    const mensaje = document.getElementById('mensaje');

    let countdown;

    const iniciarTemporizador = () => {
        let tiempo = 60;
        resendBtn.style.display = 'inline-block';
        sendBtn.style.display = 'none';
        timerSpan.textContent = tiempo;

        countdown = setInterval(() => {
            tiempo--;
            timerSpan.textContent = tiempo;
            if (tiempo <= 0) {
                clearInterval(countdown);
                resendBtn.style.display = 'none';
                sendBtn.style.display = 'inline-block';
            }
        }, 1000);
    };

    const enviar = async () => {
        const correo = correoInput.value.trim();
        if (!correo || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            mensaje.textContent = 'Introduce un correo válido.';
            return;
        }

        try {
            await peticionario.hacerPeticionRest('POST', '/api/v1/auth/forgot-password', { correo });
            mensaje.textContent = 'Enlace enviado. Revisa tu correo.';
            mensaje.style.color = 'green';
            iniciarTemporizador();
        } catch (error) {
            mensaje.textContent = 'Error: correo no registrado o fallo en el servidor.';
            console.error(error);
        }
    };

    sendBtn.addEventListener('click', enviar);
    resendBtn.addEventListener('click', enviar);
});
