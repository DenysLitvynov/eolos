// Obtener referencias a los elementos

// ❌ ERROR 1 CORREGIDO: Usar querySelectorAll en lugar de getElementsByClassName 
// y almacenamos MÚLTIPLES elementos (una NodeList)
const tarjetas = document.querySelectorAll('.tarjeta-incidencia');

const closeBtn = document.getElementById('closePopupBtn');

// ❌ ERROR 2 CORREGIDO: Usar el ID CORRECTO de tu pop-up (popup_incidencia)
const popup = document.getElementById('popup_incidencia');


// --- Funciones (se mantienen igual) ---

function openPopup() {
    popup.style.display = 'block';
}

function closePopup() {
    popup.style.display = 'none';
}


// --- Event Listeners (Control de eventos) ---

// ❌ ERROR 3 CORREGIDO: Iterar sobre la lista de tarjetas y agregar el listener a cada una
tarjetas.forEach(tarjeta => {
    tarjeta.addEventListener('click', openPopup);
});

// 2. Cerrar al hacer clic en el botón dentro del pop-up
closeBtn.addEventListener('click', closePopup);

// Opcional: Cerrar el pop-up haciendo clic fuera de su contenido (en el fondo oscuro)
window.addEventListener('click', (event) => {
    if (event.target === popup) {
        closePopup();
    }
});