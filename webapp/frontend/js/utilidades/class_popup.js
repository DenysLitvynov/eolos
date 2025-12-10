
/**========================
 * CLASE POPUP
 * =========================
 *  Clase para crear y manejar pop-ups dinámicos en la aplicación web.
 * @author Ariel Bejaran
 * @note esta clase solo vuelve divs y otras cosas en pop ups, el css se debe aplicar por separado
 * ========================
 */
export class Popup {
    /**
     * @param {string} title El título a mostrar en el encabezado del pop-up.
     * @param {HTMLElement} contentElement El elemento DIV con el contenido a mostrar.
     * 
     */
    constructor(title, contentElement) {
        //Crea la estructura HTML del pop-up
        this.popupElement = document.createElement('div');
        this.popupElement.id = 'dynamicPopup'; 
        this.popupElement.className = 'popup-container'; 

        // 2. Crear el contenido interno
        this.contentWrapper = document.createElement('div');
        this.contentWrapper.className = 'popup-content';

        // 3. Crear el título
        const titleElement = document.createElement('h1');
        titleElement.textContent = title;
    
        // 4. Crear el botón de cerrar
        const closeButton = document.createElement('button');
        closeButton.className = 'close-popup-btn fas fa-times'; // CLASE DE ICONO 'X

        // 5. Ensamblar la estructura:
        this.contentWrapper.appendChild(closeButton);
        this.contentWrapper.appendChild(titleElement);
        this.contentWrapper.appendChild(contentElement); // Añadir el DIV de contenido personalizado
        this.popupElement.appendChild(this.contentWrapper);

        // 6. Añadir el pop-up al cuerpo del documento (solo una vez)
        document.body.appendChild(this.popupElement);

        // 7. Configurar eventos de cierre
        closeButton.addEventListener('click', () => this.cerrarPopup());
        
        // Cierre al hacer clic en el fondo oscuro
        this.popupElement.addEventListener('click', (event) => {
            if (event.target === this.popupElement) {
                this.cerrarPopup();
            }
        });
    }
    abrirPopup() {
        this.popupElement.style.display = 'block';
    }

    cerrarPopup() {
        this.popupElement.style.display = 'none';
    }
}

