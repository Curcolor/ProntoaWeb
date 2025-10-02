// JavaScript específico para páginas de error
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página de error cargada');
    
    // Inicializar funcionalidades de páginas de error
    initializeErrorPage();
});

/**
 * Inicializa las funcionalidades específicas de páginas de error
 */
function initializeErrorPage() {
    setupErrorAnimations();
    setupErrorActions();
    setupAutoRedirect();
    trackErrorView();
}

/**
 * Configura animaciones adicionales para páginas de error
 */
function setupErrorAnimations() {
    const errorContainer = document.querySelector('.error-container');
    
    if (errorContainer) {
        // Agregar clase de animación después de un breve delay
        setTimeout(() => {
            errorContainer.classList.add('error-loaded');
        }, 100);
        
        // Efecto de parallax sutil en el ícono
        const errorIcon = document.querySelector('.error-icon');
        if (errorIcon) {
            window.addEventListener('mousemove', (e) => {
                const { clientX, clientY } = e;
                const { innerWidth, innerHeight } = window;
                
                const xOffset = (clientX / innerWidth - 0.5) * 10;
                const yOffset = (clientY / innerHeight - 0.5) * 10;
                
                errorIcon.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
            });
        }
    }
}

/**
 * Configura acciones específicas de botones en páginas de error
 */
function setupErrorActions() {
    // Botón de recargar página
    const reloadButton = document.querySelector('[href="javascript:location.reload()"]');
    if (reloadButton) {
        reloadButton.addEventListener('click', function(e) {
            e.preventDefault();
            showLoadingState(this);
            setTimeout(() => {
                location.reload();
            }, 500);
        });
    }
    
    // Botón de volver atrás
    const backButton = document.querySelector('[href="javascript:history.back()"]');
    if (backButton) {
        backButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // Si no hay historial, ir al inicio
                window.location.href = '/';
            }
        });
    }
    
    // Efectos hover mejorados para botones
    document.querySelectorAll('.btn-error-primary, .btn-error-secondary').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

/**
 * Configura redirección automática para ciertos errores (opcional)
 */
function setupAutoRedirect() {
    const errorCode = document.querySelector('.error-code');
    if (!errorCode) return;
    
    const code = errorCode.textContent.trim();
    
    // Para errores 500, mostrar un countdown opcional
    if (code === '500') {
        const autoRedirectEnabled = false; // Cambiar a true para habilitar
        
        if (autoRedirectEnabled) {
            let countdown = 30; // 30 segundos
            const countdownElement = document.createElement('div');
            countdownElement.className = 'mt-3 text-muted';
            countdownElement.innerHTML = `Redirección automática en <span class="fw-bold">${countdown}</span> segundos`;
            
            document.querySelector('.error-actions').appendChild(countdownElement);
            
            const timer = setInterval(() => {
                countdown--;
                countdownElement.querySelector('.fw-bold').textContent = countdown;
                
                if (countdown <= 0) {
                    clearInterval(timer);
                    window.location.href = '/';
                }
            }, 1000);
            
            // Permitir cancelar la redirección
            document.addEventListener('click', () => {
                clearInterval(timer);
                countdownElement.remove();
            });
        }
    }
}

/**
 * Rastrea la visualización de errores para analytics
 */
function trackErrorView() {
    const errorCode = document.querySelector('.error-code');
    if (!errorCode) return;
    
    const code = errorCode.textContent.trim();
    const errorData = {
        error_code: code,
        page_url: window.location.href,
        referrer: document.referrer || 'direct',
        timestamp: new Date().toISOString()
    };
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'error_page_view', {
            'error_code': code,
            'page_location': window.location.href,
            'custom_map': {
                'custom_parameter_1': 'error_type'
            }
        });
    }
    
    // Tracking personalizado (opcional)
    console.log('Error page view tracked:', errorData);
    
    // Enviar a servidor para logging (opcional)
    if (navigator.sendBeacon) {
        const formData = new FormData();
        formData.append('error_data', JSON.stringify(errorData));
        // navigator.sendBeacon('/api/log-error', formData);
    }
}

/**
 * Muestra estado de carga en un botón
 */
function showLoadingState(button) {
    const originalText = button.innerHTML;
    const loadingText = '<i class="fas fa-spinner fa-spin me-2"></i>Cargando...';
    
    button.innerHTML = loadingText;
    button.disabled = true;
    
    // Restaurar estado original después de 5 segundos (fallback)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 5000);
}

/**
 * Reportar error adicional (para debugging)
 */
function reportError(errorDetails) {
    const errorReport = {
        ...errorDetails,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        url: window.location.href
    };
    
    console.error('Error report:', errorReport);
    
    // Enviar reporte al servidor (opcional)
    // fetch('/api/error-report', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(errorReport)
    // });
}

/**
 * Agregar información de debug (solo en desarrollo)
 */
function addDebugInfo() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const debugInfo = document.createElement('div');
        debugInfo.className = 'mt-4 p-3 bg-light border rounded text-start';
        debugInfo.innerHTML = `
            <h6>Debug Info (Development)</h6>
            <small>
                <strong>URL:</strong> ${window.location.href}<br>
                <strong>Referrer:</strong> ${document.referrer || 'None'}<br>
                <strong>User Agent:</strong> ${navigator.userAgent}<br>
                <strong>Timestamp:</strong> ${new Date().toLocaleString()}
            </small>
        `;
        
        const errorContainer = document.querySelector('.error-container');
        if (errorContainer) {
            errorContainer.appendChild(debugInfo);
        }
    }
}

// Exportar funciones para uso global
window.ErrorPage = {
    reportError,
    showLoadingState
};

// Ejecutar debug info si estamos en desarrollo
addDebugInfo();
