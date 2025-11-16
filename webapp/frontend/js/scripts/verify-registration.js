/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Handlers para verify-registration.html. Solo interfaz.
*/

import { VerifyFake } from '../logica_fake/verify_registration_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const fake = new VerifyFake();
    const codigoInput = document.getElementById('codigo');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendBtn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');
    const mensaje = document.getElementById('mensaje');

    const correo = localStorage.getItem('pending_email');
    if (!correo) {
        mensaje.textContent = 'Sesión expirada. Regístrate de nuevo.';
        verifyBtn.disabled = true;
        return;
    }

    let countdown;

    const iniciarTemporizador = () => {
        let tiempo = 60;
        resendBtn.style.display = 'inline-block';
        verifyBtn.style.display = 'none';
        timerSpan.textContent = tiempo;
        countdown = setInterval(() => {
            tiempo--;
            timerSpan.textContent = tiempo;
            if (tiempo <= 0) {
                clearInterval(countdown);
                resendBtn.style.display = 'none';
                verifyBtn.style.display = 'inline-block';
            }
        }, 1000);
    };

    verifyBtn.addEventListener('click', async () => {
        const verification_code = codigoInput.value.trim();
        if (!/^\d{6}$/.test(verification_code)) {
            mensaje.textContent = 'Código debe tener 6 dígitos.';
            return;
        }

        try {
            const res = await fake.verificar(correo, verification_code);
            localStorage.setItem('token', res.token);
            localStorage.removeItem('pending_email');
            mensaje.textContent = '¡Registro completado! Redirigiendo...';
            mensaje.style.color = 'green';
            setTimeout(() => { window.location.href = '/pages/prueba.html'; }, 2000);
        } catch (error) {
            mensaje.textContent = 'Código incorrecto o expirado.';
        }
    });

    resendBtn.addEventListener('click', async () => {
        try {
            await fake.reenviar(correo);
            mensaje.textContent = 'Código reenviado.';
            mensaje.style.color = 'green';
            iniciarTemporizador();
        } catch (error) {
            mensaje.textContent = 'Error al reenviar.';
        }
    });
});
