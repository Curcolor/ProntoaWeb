// Profile JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile page loaded');
    
    // Inicializar animaciones de métricas
    initializeMetricsAnimations();
    
    // Configurar tooltips
    initializeTooltips();
});

function initializeMetricsAnimations() {
    const metricValues = document.querySelectorAll('.metric-value');
    
    // Observador de intersección para animar cuando entren en vista
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateMetricValue(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    metricValues.forEach(metric => {
        observer.observe(metric);
    });
}

function animateMetricValue(element) {
    const finalValue = element.textContent;
    const isNumeric = /^\d+(\.\d+)?/.test(finalValue);
    
    if (isNumeric) {
        const numericValue = parseFloat(finalValue);
        const duration = 1500; // 1.5 segundos
        const startTime = performance.now();
        
        function updateValue(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Función de easing
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = numericValue * easeOutQuart;
            
            if (finalValue.includes('.')) {
                element.textContent = currentValue.toFixed(1) + finalValue.slice(-3); // Mantener 'min' o similar
            } else {
                element.textContent = Math.floor(currentValue) + finalValue.slice(-1); // Mantener unidad
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateValue);
            } else {
                element.textContent = finalValue; // Asegurar valor final exacto
            }
        }
        
        requestAnimationFrame(updateValue);
    }
}

function initializeTooltips() {
    // Configurar tooltips para los iconos de información
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    // Posicionar tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    // Animar entrada
    requestAnimationFrame(() => {
        tooltip.classList.add('visible');
    });
    
    element._tooltip = tooltip;
}

function hideTooltip(e) {
    const element = e.target;
    const tooltip = element._tooltip;
    
    if (tooltip) {
        tooltip.classList.remove('visible');
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 200);
        delete element._tooltip;
    }
}

// Función para actualizar información del perfil
function updateProfileInfo(field, value) {
    const infoElement = document.querySelector(`[data-field="${field}"] .info-value`);
    if (infoElement) {
        infoElement.textContent = value;
        
        // Animación de actualización
        infoElement.style.opacity = '0.5';
        setTimeout(() => {
            infoElement.style.opacity = '1';
        }, 300);
    }
}

// Función para simular actualización de métricas en tiempo real
function simulateRealTimeUpdates() {
    setInterval(() => {
        const timeMetric = document.querySelector('.metric-item.primary .metric-value');
        const ordersMetric = document.querySelector('.metric-item.info .metric-value');
        
        if (timeMetric) {
            const currentTime = parseFloat(timeMetric.textContent);
            const variation = (Math.random() - 0.5) * 0.2; // Variación de ±0.1 min
            const newTime = Math.max(1.0, currentTime + variation);
            timeMetric.textContent = newTime.toFixed(1) + 'min';
        }
        
        if (ordersMetric) {
            const currentOrders = parseInt(ordersMetric.textContent);
            const shouldUpdate = Math.random() < 0.3; // 30% de probabilidad
            if (shouldUpdate) {
                ordersMetric.textContent = currentOrders + 1;
            }
        }
    }, 10000); // Actualizar cada 10 segundos
}

// Inicializar actualizaciones simuladas
setTimeout(simulateRealTimeUpdates, 5000);