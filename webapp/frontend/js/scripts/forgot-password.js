/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para forgot-password.html. Solo interfaz.
*/

import { ForgotPasswordFake } from '../logica_fake/forgot_password_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const fake = new ForgotPasswordFake();
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
            await fake.enviar(correo);
            mensaje.textContent = 'Enlace enviado. Revisa tu correo.';
            mensaje.style.color = 'green';
            iniciarTemporizador();
        } catch (error) {
            mensaje.textContent = 'Correo no registrado.';
        }
    };

    sendBtn.addEventListener('click', enviar);
    resendBtn.addEventListener('click', enviar);
});
