/**
 * CSRF Token Helper
 * Proporciona funciones para obtener y usar el token CSRF en peticiones AJAX
 */

/**
 * Obtiene el token CSRF del meta tag
 * @returns {string|null} El token CSRF o null si no existe
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

/**
 * Crea headers con CSRF token para peticiones fetch
 * @param {Object} additionalHeaders - Headers adicionales opcionales
 * @returns {Object} Headers con CSRF token incluido
 */
function getCsrfHeaders(additionalHeaders = {}) {
    const token = getCsrfToken();
    return {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token,
        ...additionalHeaders
    };
}

/**
 * Wrapper de fetch que incluye automáticamente CSRF token en peticiones POST/PUT/PATCH/DELETE
 * @param {string} url - URL de la petición
 * @param {Object} options - Opciones de fetch
 * @returns {Promise<Response>}
 */
async function fetchWithCsrf(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    
    // Solo agregar CSRF token en métodos que modifican datos
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const token = getCsrfToken();
        
        options.headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            'X-CSRF-Token': token
        };
        
        // Asegurar credentials para cookies de sesión
        options.credentials = options.credentials || 'include';
    }
    
    return fetch(url, options);
}

/**
 * Configura axios para incluir CSRF token automáticamente (si se usa axios)
 */
function setupAxiosCsrf() {
    if (typeof axios !== 'undefined') {
        const token = getCsrfToken();
        if (token) {
            axios.defaults.headers.common['X-CSRF-Token'] = token;
        }
    }
}

// Auto-configurar axios si está disponible
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAxiosCsrf);
} else {
    setupAxiosCsrf();
}

// Exportar funciones para uso en módulos ES6 (si se necesita)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCsrfToken,
        getCsrfHeaders,
        fetchWithCsrf,
        setupAxiosCsrf
    };
}
