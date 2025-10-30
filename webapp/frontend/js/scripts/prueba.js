/* 
Autor: Denys Litvynov Lymanets
Fecha: 27-10-2025
Descripción: Handlers para prueba.html. Verifica token y maneja logout.
*/

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const mensaje = document.getElementById('mensaje');
    const logoutBtn = document.getElementById('logoutBtn');

    // Verificar si hay token
    if (!token) {
        mensaje.textContent = 'No estás autenticado. Redirigiendo al login...';
        window.setTimeout(() => { window.location.href = '/pages/login.html'; }, 1000);
        return;
    }

    // Mostrar mensaje de éxito
    mensaje.textContent = 'Sesión activa. PRUEBA.';

    // Manejar logout
    logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('token');
        mensaje.textContent = 'Sesión cerrada. Redirigiendo...';
        window.setTimeout(() => { window.location.href = '/'; }, 1000);
    });
});
