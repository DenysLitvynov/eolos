/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Script que controla forgot-password.html: envío del correo, temporizador de 60s y reenvío.
*/

import { ForgotPasswordFake } from '../logica_fake/forgot_password_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const fake = new ForgotPasswordFake();
    const correoInput = document.getElementById('correo');
    const sendBtn = document.getElementById('sendBtn');
    const resendBtn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');
    const mensaje = document.getElementById('mensaje');
    const correoError = document.getElementById('correoError');

    let countdown;
    let tiempoRestante = 60;

    // TEMPORIZADOR RESTAURADO
    const iniciarTemporizador = () => {
        tiempoRestante = 60;
        resendBtn.style.display = 'none';
        sendBtn.style.display = 'inline-block';
        timerSpan.textContent = tiempoRestante;
        timerSpan.style.display = 'inline';
        
        countdown = setInterval(() => {
            tiempoRestante--;
            timerSpan.textContent = tiempoRestante;
            
            if (tiempoRestante <= 0) {
                clearInterval(countdown);
                resendBtn.style.display = 'inline-block';
                sendBtn.style.display = 'none';
                timerSpan.style.display = 'none';
            }
        }, 1000);
    };

    // Validación básica en tiempo real del correo
    correoInput.addEventListener('blur', () => {
        const correo = correoInput.value.trim();
        if (!correo) {
            mostrarError(correoError, 'El correo electrónico es obligatorio');
            correoInput.classList.add('error');
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            mostrarError(correoError, 'Formato de correo electrónico inválido');
            correoInput.classList.add('error');
        } else {
            ocultarError(correoError);
            correoInput.classList.remove('error');
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

    const enviar = async () => {
        const correo = correoInput.value.trim();
        
        // Validación básica
        if (!correo) {
            mostrarError(correoError, 'El correo electrónico es obligatorio');
            correoInput.classList.add('error');
            return;
        }
        
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            mostrarError(correoError, 'Formato de correo electrónico inválido');
            correoInput.classList.add('error');
            return;
        }

        try {
            mensaje.textContent = 'Enviando enlace de recuperación...';
            mensaje.style.color = '#666';

            await fake.enviar(correo);
            
            // Mensaje genérico para seguridad (no revelar si el correo existe)
            mensaje.textContent = 'Si el correo está registrado, recibirás un enlace de recuperación.';
            mensaje.style.color = 'green';
            
            iniciarTemporizador();
            
        } catch (error) {
            // Mensaje genérico igual para todos los casos
            mensaje.textContent = 'Si el correo está registrado, recibirás un enlace de recuperación.';
            mensaje.style.color = 'green';
            console.error('Error detallado en forgot password:', error);
        }
    };

    sendBtn.addEventListener('click', enviar);
    resendBtn.addEventListener('click', enviar);

    // Permitir envío con Enter
    correoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });
});
