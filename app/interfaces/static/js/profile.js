// Profile JavaScript - Conectado a API REST real
document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile page loaded - Using real API');
    
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
        
        // Cargar datos del usuario y métricas en paralelo
        const [userResult, metricsResult] = await Promise.all([
            fetchCurrentUser(),
            fetchDashboardMetrics()
        ]);
        
        if (userResult.success) {
            updateProfileInfo(userResult.user);
            updateBusinessInfo(userResult.business);
        }
        
        if (metricsResult.success) {
            updateProfileMetrics(metricsResult.metrics);
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
        const result = await fetchDashboardMetrics();
        
        if (result.success) {
            updateProfileMetrics(result.metrics);
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
    
    // Nombre completo
    const fullNameEl = document.getElementById('user-full-name');
    if (fullNameEl && user.full_name) {
        fullNameEl.textContent = user.full_name;
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
    
    // Fecha de registro
    const registeredEl = document.getElementById('user-registered');
    if (registeredEl && user.created_at) {
        registeredEl.textContent = formatDate(user.created_at);
    }
    
    // Último login
    const lastLoginEl = document.getElementById('user-last-login');
    if (lastLoginEl && user.last_login) {
        lastLoginEl.textContent = formatDate(user.last_login);
    }
}

function updateBusinessInfo(business) {
    if (!business) return;
    
    // Nombre del negocio
    const businessNameEl = document.getElementById('business-name');
    if (businessNameEl && business.name) {
        businessNameEl.textContent = business.name;
    }
    
    // Tipo de negocio
    const businessTypeEl = document.getElementById('business-type');
    if (businessTypeEl && business.business_type) {
        businessTypeEl.textContent = getBusinessTypeLabel(business.business_type);
    }
    
    // Ubicación
    const locationEl = document.getElementById('business-location');
    if (locationEl && business.location) {
        locationEl.textContent = business.location;
    }
    
    // Plan de suscripción
    const planEl = document.getElementById('subscription-plan');
    if (planEl && business.subscription_plan) {
        planEl.textContent = getPlanLabel(business.subscription_plan);
    }
}

function updateProfileMetrics(metrics) {
    // Tiempo promedio de respuesta
    const avgResponseEl = document.querySelector('.metric-item.primary .metric-value');
    if (avgResponseEl && metrics.avg_response_time !== undefined) {
        avgResponseEl.textContent = metrics.avg_response_time.toFixed(1) + 'min';
    }
    
    // Pedidos procesados hoy
    const ordersEl = document.querySelector('.metric-item.info .metric-value');
    if (ordersEl && metrics.orders_today !== undefined) {
        ordersEl.textContent = metrics.orders_today;
    }
    
    // Satisfacción del cliente
    const satisfactionEl = document.querySelector('.metric-item.success .metric-value');
    if (satisfactionEl && metrics.satisfaction !== undefined) {
        satisfactionEl.textContent = metrics.satisfaction.toFixed(1) + '%';
    }
    
    // Ventas de hoy
    const salesEl = document.querySelector('.metric-item.warning .metric-value');
    if (salesEl && metrics.sales_today !== undefined) {
        salesEl.textContent = formatCurrency(metrics.sales_today);
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