// JavaScript principal para ProntoaWeb
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ProntoaWeb cargado correctamente');
    
    // Inicializar componentes
    initializeApp();
});

/**
 * Inicializa los componentes principales de la aplicación
 */
function initializeApp() {
    // Agregar animaciones de fade-in a elementos
    addFadeInAnimations();
    
    // Configurar manejadores de eventos
    setupEventHandlers();
    
    // Configurar llamadas a API si es necesario
    setupAPIHandlers();
}

/**
 * Agrega animaciones de fade-in a elementos con la clase correspondiente
 */
function addFadeInAnimations() {
    const elements = document.querySelectorAll('.card, .alert, main > *');
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Configura manejadores de eventos globales
 */
function setupEventHandlers() {
    // Mejorar experiencia de botones
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Agregar efecto de ripple (opcional)
            addRippleEffect(this, e);
        });
    });
    
    // Manejar enlaces de navegación
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Remover clase active de todos los enlaces
            navLinks.forEach(l => l.classList.remove('active'));
            // Agregar clase active al enlace clickeado
            this.classList.add('active');
        });
    });
}

/**
 * Configura manejadores para llamadas a la API
 */
function setupAPIHandlers() {
    // Configuración base para llamadas a API
    window.API = {
        baseURL: '/api',
        
        /**
         * Realiza una llamada GET a la API
         * @param {string} endpoint - Endpoint a llamar
         * @returns {Promise} Respuesta de la API
         */
        async get(endpoint) {
            try {
                const response = await fetch(`${this.baseURL}${endpoint}`);
                return await response.json();
            } catch (error) {
                console.error('Error en llamada GET:', error);
                throw error;
            }
        },
        
        /**
         * Realiza una llamada POST a la API
         * @param {string} endpoint - Endpoint a llamar
         * @param {Object} data - Datos a enviar
         * @returns {Promise} Respuesta de la API
         */
        async post(endpoint, data) {
            try {
                const response = await fetch(`${this.baseURL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                console.error('Error en llamada POST:', error);
                throw error;
            }
        }
    };
}

/**
 * Agrega efecto de ripple a un botón
 * @param {Element} button - Elemento del botón
 * @param {Event} event - Evento de click
 */
function addRippleEffect(button, event) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Utilidad para mostrar notificaciones toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, info)
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-in');
    }, 100);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Utilidad para formatear fechas
 * @param {Date} date - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Exportar utilidades para uso global
window.ProntoaWeb = {
    showToast,
    formatDate,
    API: window.API
};
