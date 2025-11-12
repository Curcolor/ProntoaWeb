// Profile JavaScript - Conectado a API REST real
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos del usuario y métricas
    loadProfileData();
    
    // Inicializar animaciones
    initializeMetricsAnimations();
    
    // Configurar tooltips
    initializeTooltips();
    
    // Setup event listeners
    setupEventListeners();
    
    // Actualizar cada 60 segundos
    setInterval(loadProfileMetrics, 60000);
});

// ============================================================
// CARGAR DATOS DEL PERFIL
// ============================================================

async function loadProfileData() {
    try {
        showLoadingState();
        
        // Cargar datos del usuario, negocio y métricas KPI completas
        const [userResult, kpiResult] = await Promise.all([
            fetchCurrentUser(),
            fetchKPISummary()
        ]);
        
        if (userResult.success) {
            updateProfileInfo(userResult.user);
            if (userResult.business) {
                updateBusinessInfo(userResult.business);
            }
        }
        
        if (kpiResult.success && kpiResult.summary) {
            updateProfileMetrics(kpiResult.summary.dashboard);
            updateOptimizationMetrics(kpiResult.summary.comparisons);
        }
        
        hideLoadingState();
        
    } catch (error) {
        console.error('Error loading profile:', error);
        showNotification('Error al cargar el perfil', 'error');
        hideLoadingState();
    }
}

async function loadProfileMetrics() {
    try {
        const result = await fetchKPISummary();
        
        if (result.success && result.summary) {
            updateProfileMetrics(result.summary.dashboard);
            updateOptimizationMetrics(result.summary.comparisons);
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

// ============================================================
// API CALLS
// ============================================================

async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/auth/me', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar usuario');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching user:', error);
        return { success: false, message: error.message };
    }
}

async function fetchDashboardMetrics() {
    try {
        const response = await fetch('/api/kpis/dashboard', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar métricas');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching metrics:', error);
        return { success: false, message: error.message };
    }
}

async function fetchKPISummary() {
    try {
        const response = await fetch('/api/kpis/summary', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar métricas');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching KPI summary:', error);
        return { success: false, message: error.message };
    }
}

async function updateUserProfile(profileData) {
    try {
        const response = await fetch('/api/auth/profile', {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al actualizar perfil');
        }
        
        return data;
    } catch (error) {
        console.error('Error updating profile:', error);
        return { success: false, message: error.message };
    }
}

// ============================================================
// UPDATE UI FUNCTIONS
// ============================================================

function updateProfileInfo(user) {
    if (!user) return;
    
    // Nombre completo en header
    const headerNameEl = document.getElementById('profile-header-name');
    if (headerNameEl && user.full_name) {
        headerNameEl.textContent = user.full_name;
    }
    
    // Inicial del avatar
    const avatarInitialEl = document.getElementById('user-avatar-initial');
    if (avatarInitialEl && user.full_name) {
        avatarInitialEl.textContent = user.full_name.charAt(0).toUpperCase();
    }
    
    // Email
    const emailEl = document.getElementById('user-email');
    if (emailEl && user.email) {
        emailEl.textContent = user.email;
    }
    
    // Teléfono
    const phoneEl = document.getElementById('user-phone');
    if (phoneEl && user.phone) {
        phoneEl.textContent = user.phone;
    }
}

function updateBusinessInfo(business) {
    if (!business) return;
    
    // Nombre del negocio
    const businessNameEl = document.getElementById('business-name');
    if (businessNameEl && business.name) {
        businessNameEl.textContent = business.name;
    }
    
    // Subtítulo del header (Propietario - Negocio)
    const headerSubtitleEl = document.getElementById('profile-header-subtitle');
    if (headerSubtitleEl && business.name) {
        headerSubtitleEl.textContent = `Propietario - ${business.name}`;
    }
    
    // Tipo de negocio en badge
    const badgeTypeEl = document.getElementById('badge-business-type');
    if (badgeTypeEl && business.business_type) {
        badgeTypeEl.textContent = getBusinessTypeLabel(business.business_type);
    }
    
    // Ubicación (combinar address y city)
    const locationEl = document.getElementById('business-location');
    if (locationEl) {
        const location = business.city ? `${business.address || ''}, ${business.city}` : business.address;
        if (location) {
            locationEl.textContent = location;
        }
    }
}

function updateProfileMetrics(metrics) {
    if (!metrics) return;
    
    // Tiempo promedio de respuesta
    const avgResponseEl = document.getElementById('metric-avg-response');
    if (avgResponseEl) {
        const minutes = parseFloat(metrics.avg_response_time) || 0;
        avgResponseEl.textContent = minutes.toFixed(1) + 'min';
    }
    
    // Pedidos procesados hoy
    const ordersEl = document.getElementById('metric-orders-today');
    if (ordersEl) {
        ordersEl.textContent = parseInt(metrics.orders_today) || 0;
    }
    
    // Satisfacción del cliente
    const satisfactionEl = document.getElementById('metric-satisfaction');
    if (satisfactionEl) {
        const satisfaction = parseFloat(metrics.satisfaction) || 0;
        satisfactionEl.textContent = satisfaction.toFixed(1);
    }
}

function updateOptimizationMetrics(comparisons) {
    if (!comparisons) return;
    
    // Reducción de tiempo de respuesta
    const responseTimeEl = document.getElementById('optimization-response-time');
    if (responseTimeEl && comparisons.response_time) {
        const reduction = parseFloat(comparisons.response_time.change) || 0;
        responseTimeEl.textContent = (reduction >= 0 ? '+' : '') + reduction.toFixed(1) + '%';
    }
    
    // Aumento en ventas
    const salesEl = document.getElementById('optimization-sales');
    if (salesEl && comparisons.orders_processed) {
        const increase = parseFloat(comparisons.orders_processed.change) || 0;
        salesEl.textContent = (increase >= 0 ? '+' : '') + increase.toFixed(1) + '%';
    }
    
    // Mejora en satisfacción
    const satisfactionEl = document.getElementById('optimization-satisfaction');
    if (satisfactionEl && comparisons.satisfaction) {
        const improvement = parseFloat(comparisons.satisfaction.change) || 0;
        satisfactionEl.textContent = (improvement >= 0 ? '+' : '') + improvement.toFixed(1) + '%';
    }
}

// ============================================================
// EVENT LISTENERS
// ============================================================

function setupEventListeners() {
    // Botón de editar perfil
    const editBtn = document.getElementById('edit-profile-btn');
    if (editBtn) {
        editBtn.addEventListener('click', enableProfileEditing);
    }
    
    // Botón de guardar cambios
    const saveBtn = document.getElementById('save-profile-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', handleSaveProfile);
    }
    
    // Botón de cancelar edición
    const cancelBtn = document.getElementById('cancel-edit-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', disableProfileEditing);
    }
}

function enableProfileEditing() {
    // Hacer campos editables
    const editableFields = document.querySelectorAll('[data-editable]');
    editableFields.forEach(field => {
        const value = field.textContent;
        const input = document.createElement('input');
        input.type = 'text';
        input.value = value;
        input.className = 'form-control';
        input.dataset.fieldName = field.dataset.editable;
        
        field.replaceWith(input);
    });
    
    // Mostrar botones de guardar/cancelar
    document.getElementById('edit-profile-btn')?.classList.add('d-none');
    document.getElementById('save-profile-btn')?.classList.remove('d-none');
    document.getElementById('cancel-edit-btn')?.classList.remove('d-none');
}

function disableProfileEditing() {
    // Recargar datos originales
    loadProfileData();
    
    // Ocultar botones de guardar/cancelar
    document.getElementById('save-profile-btn')?.classList.add('d-none');
    document.getElementById('cancel-edit-btn')?.classList.add('d-none');
    document.getElementById('edit-profile-btn')?.classList.remove('d-none');
}

async function handleSaveProfile() {
    // Recopilar datos de los campos editables
    const inputs = document.querySelectorAll('input[data-field-name]');
    const profileData = {};
    
    inputs.forEach(input => {
        profileData[input.dataset.fieldName] = input.value;
    });
    
    // Guardar en el servidor
    const result = await updateUserProfile(profileData);
    
    if (result.success) {
        showNotification('Perfil actualizado correctamente', 'success');
        loadProfileData();
        disableProfileEditing();
    } else {
        showNotification(result.message || 'Error al actualizar perfil', 'error');
    }
}

// ============================================================
// ANIMATIONS
// ============================================================

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
                element.textContent = currentValue.toFixed(1) + (finalValue.match(/[a-z%]+$/i)?.[0] || '');
            } else {
                element.textContent = Math.floor(currentValue) + (finalValue.match(/[a-z%]+$/i)?.[0] || '');
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

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount || 0);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function getBusinessTypeLabel(type) {
    const types = {
        restaurant: 'Restaurante',
        bakery: 'Panadería',
        cafe: 'Cafetería',
        store: 'Tienda',
        pharmacy: 'Farmacia',
        other: 'Otro'
    };
    return types[type] || type;
}

function getPlanLabel(plan) {
    const plans = {
        free: 'Gratis',
        basic: 'Básico',
        premium: 'Premium',
        enterprise: 'Empresarial'
    };
    return plans[plan] || plan;
}

function showLoadingState() {
    const container = document.querySelector('.profile-container');
    if (container) {
        container.style.opacity = '0.6';
        container.style.pointerEvents = 'none';
    }
}

function hideLoadingState() {
    const container = document.querySelector('.profile-container');
    if (container) {
        container.style.opacity = '1';
        container.style.pointerEvents = 'auto';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}