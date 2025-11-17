/* 
Autor: Denys Litvynov Lymanets
Fecha: 16-11-2025
Descripción: Script que maneja la interfaz de verificación de código: temporizador, validaciones en frontend, envío del código y reenvío, redirigiendo si todo sale bien.
*/

// ----------------------------------------------------------

import { VerifyFake } from '../logica_fake/verify_registration_fake.js';

document.addEventListener('DOMContentLoaded', () => {
    const fake = new VerifyFake();
    const codigoInput = document.getElementById('codigo');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendBtn = document.getElementById('resendBtn');
    const timerSpan = document.getElementById('timer');
    const mensaje = document.getElementById('mensaje');
    const codigoError = document.getElementById('codigoError');

    const correo = localStorage.getItem('pending_email');
    if (!correo) {
        mensaje.textContent = 'Sesión expirada. Por favor, completa el registro nuevamente.';
        mensaje.style.color = '#d32f2f';
        verifyBtn.disabled = true;
        resendBtn.disabled = true;
        return;
    }

    let countdown;
    let tiempoRestante = 60;

// ----------------------------------------------------------
// Método que inicia y maneja un temporizador de 60 segundos, mostrando botones según el estado.
//
// -> iniciarTemporizador() -> void
// ----------------------------------------------------------
    // TEMPORIZADOR RESTAURADO: Iniciar temporizador al cargar
    const iniciarTemporizador = () => {
        tiempoRestante = 60;
        resendBtn.style.display = 'none';
        verifyBtn.style.display = 'inline-block';
        timerSpan.textContent = tiempoRestante;
        timerSpan.style.display = 'inline';
        
        countdown = setInterval(() => {
            tiempoRestante--;
            timerSpan.textContent = tiempoRestante;
            
            if (tiempoRestante <= 0) {
                clearInterval(countdown);
                resendBtn.style.display = 'inline-block';
                verifyBtn.style.display = 'none';
                timerSpan.style.display = 'none';
            }
        }, 1000);
    };

    // Iniciar temporizador al cargar
    iniciarTemporizador();

    // Validación básica en tiempo real del código
    codigoInput.addEventListener('blur', () => {
        const codigo = codigoInput.value.trim();
        if (!codigo) {
            mostrarError(codigoError, 'El código de verificación es obligatorio');
            codigoInput.classList.add('error');
        } else if (!/^\d{6}$/.test(codigo)) {
            mostrarError(codigoError, 'El código debe tener 6 dígitos');
            codigoInput.classList.add('error');
        } else {
            ocultarError(codigoError);
            codigoInput.classList.remove('error');
        }
    });

// ----------------------------------------------------------
// Método que muestra un mensaje de error en un elemento y añade clase de error.
//
// elemento : HTMLElement
// mensaje : string
// -> mostrarError() -> void
// ----------------------------------------------------------
    function mostrarError(elemento, mensaje) {
        elemento.textContent = mensaje;
        elemento.classList.add('show');
    }

// ----------------------------------------------------------
// Método que oculta un mensaje de error en un elemento y quita clase de error.
//
// elemento : HTMLElement
// -> ocultarError() -> void
// ----------------------------------------------------------
    function ocultarError(elemento) {
        elemento.textContent = '';
        elemento.classList.remove('show');
    }

// ----------------------------------------------------------
// Método que valida si el código es obligatorio y tiene 6 dígitos, mostrando errores si no.
//
// -> validarCodigo() -> boolean
// ----------------------------------------------------------
    function validarCodigo() {
        const codigo = codigoInput.value.trim();
        if (!codigo) {
            mostrarError(codigoError, 'El código de verificación es obligatorio');
            codigoInput.classList.add('error');
            return false;
        }
        if (!/^\d{6}$/.test(codigo)) {
            mostrarError(codigoError, 'El código debe tener 6 dígitos');
            codigoInput.classList.add('error');
            return false;
        }
        return true;
    }

    verifyBtn.addEventListener('click', async () => {
        if (!validarCodigo()) {
            return;
        }

        const verification_code = codigoInput.value.trim();

        try {
            mensaje.textContent = 'Verificando código...';
            mensaje.style.color = '#666';

            const res = await fake.verificar(correo, verification_code);
            localStorage.setItem('token', res.token);
            localStorage.removeItem('pending_email');
            
            mensaje.textContent = '¡¡Registro completado exitosamente! Redirigiendo...';
            mensaje.style.color = 'green';
            
            setTimeout(() => { 
                window.location.href = '/pages/prueba.html'; 
            }, 2000);
            
        } catch (error) {
            // Mensaje genérico para seguridad
            mensaje.textContent = 'Código incorrecto o expirado. Verifica el código e intenta nuevamente.';
            mensaje.style.color = '#d32f2f';
            codigoInput.classList.add('error');
            console.error('Error detallado en verify registration:', error);
        }
    });

    resendBtn.addEventListener('click', async () => {
        try {
            mensaje.textContent = 'Reenviando código...';
            mensaje.style.color = '#666';

            await fake.reenviar(correo);
            
            mensaje.textContent = 'Código reenviado. Revisa tu correo electrónico.';
            mensaje.style.color = 'green';
            
            // Reiniciar temporizador
            clearInterval(countdown);
            iniciarTemporizador();
            
        } catch (error) {
            mensaje.textContent = 'Error al reenviar el código. Intenta nuevamente.';
            mensaje.style.color = '#d32f2f';
            console.error('Error detallado al reenviar código:', error);
        }
    });

    // Permitir envío con Enter
    codigoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            verifyBtn.click();
        }
    });
});
