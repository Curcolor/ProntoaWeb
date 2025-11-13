// Settings JavaScript - Conectado a API REST real
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page loaded - Using real API');
    
    // Cargar configuraciones del servidor
    loadSettings();
    
    // Inicializar configuraciones
    initializeSettings();
    
    // Configurar event listeners
    setupEventListeners();
});

// ============================================================
// CARGAR CONFIGURACIONES DESDE LA API
// ============================================================

async function loadSettings() {
    try {
        showLoadingState();
        
        // Cargar usuario y configuraciones del negocio
        const result = await fetchCurrentUser();
        
        if (result.success) {
            updateBusinessSettings(result.business);
            updateUserSettings(result.user);
        }
        
        hideLoadingState();
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showNotification('Error al cargar configuraciones', 'error');
        hideLoadingState();
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
            throw new Error(data.message || 'Error al cargar configuraciones');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching user:', error);
        return { success: false, message: error.message };
    }
}

async function updateBusinessSettings(settingsData) {
    try {
        const token = getCsrfToken();
        const response = await fetch('/api/business/settings', {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            body: JSON.stringify(settingsData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al actualizar configuraciones');
        }
        
        return data;
    } catch (error) {
        console.error('Error updating business settings:', error);
        return { success: false, message: error.message };
    }
}

// ============================================================
// UPDATE UI FUNCTIONS
// ============================================================

function updateBusinessSettings(business) {
    if (!business) return;
    
    // Nombre del negocio
    const businessNameInput = document.getElementById('business-name');
    if (businessNameInput && business.name) {
        businessNameInput.value = business.name;
    }
    
    // Tipo de negocio
    const businessTypeSelect = document.getElementById('business-type');
    if (businessTypeSelect && business.business_type) {
        businessTypeSelect.value = business.business_type;
    }
    
    // Ubicación
    const locationInput = document.getElementById('location');
    if (locationInput && business.location) {
        locationInput.value = business.location;
    }
    
    // Horarios
    const openTimeInput = document.getElementById('open-time');
    if (openTimeInput && business.opening_time) {
        openTimeInput.value = business.opening_time;
    }
    
    const closeTimeInput = document.getElementById('close-time');
    if (closeTimeInput && business.closing_time) {
        closeTimeInput.value = business.closing_time;
    }
    
    // Delivery
    const deliveryEnabledToggle = document.getElementById('delivery-enabled');
    if (deliveryEnabledToggle) {
        deliveryEnabledToggle.checked = business.delivery_enabled || false;
    }
    
    // Radio de entrega
    const deliveryRadiusInput = document.getElementById('delivery-radius');
    if (deliveryRadiusInput && business.delivery_radius_km) {
        deliveryRadiusInput.value = business.delivery_radius_km;
    }
    
    // Tarifa de delivery
    const deliveryFeeInput = document.getElementById('delivery-fee');
    if (deliveryFeeInput && business.delivery_fee) {
        deliveryFeeInput.value = business.delivery_fee;
    }
    
    // Notificaciones
    const notificationsToggle = document.getElementById('notifications-enabled');
    if (notificationsToggle) {
        notificationsToggle.checked = business.notifications_enabled !== false;
    }
    
    // WhatsApp
    const whatsappToggle = document.getElementById('whatsapp-enabled');
    if (whatsappToggle) {
        whatsappToggle.checked = business.whatsapp_enabled !== false;
    }
}


function updateUserSettings(user) {
    if (!user) return;
    
    // Email
    const emailInput = document.getElementById('user-email');
    if (emailInput && user.email) {
        emailInput.value = user.email;
    }
    
    // Nombre completo
    const fullNameInput = document.getElementById('user-full-name');
    if (fullNameInput && user.full_name) {
        fullNameInput.value = user.full_name;
    }
    
    // Teléfono
    const phoneInput = document.getElementById('user-phone');
    if (phoneInput && user.phone) {
        phoneInput.value = user.phone;
    }
}

// ============================================================
// INITIALIZE SETTINGS
// ============================================================

function initializeSettings() {
    // Inicializar toggles
    const toggles = document.querySelectorAll('.toggle input[type="checkbox"]');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', handleToggleChange);
    });
    
    // Inicializar botones de paginación
    const paginationBtns = document.querySelectorAll('.pagination-btn');
    paginationBtns.forEach(btn => {
        btn.addEventListener('click', handlePaginationChange);
    });
    
    // Inicializar selects
    const selects = document.querySelectorAll('.form-select');
    selects.forEach(select => {
        select.addEventListener('change', handleSelectChange);
    });
}

function setupEventListeners() {
    // Botón de guardar cambios
    const saveBtn = document.querySelector('.btn-save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAllSettings);
    }
    
    // Botón de restaurar valores
    const resetBtn = document.querySelector('.btn-reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetToDefaults);
    }
    
    // Botones de editar plantilla
    const editBtns = document.querySelectorAll('.btn-edit-template');
    editBtns.forEach(btn => {
        btn.addEventListener('click', editTemplate);
    });
    
    // Form de cambio de contraseña
    const passwordForm = document.getElementById('change-password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handleChangePassword);
    }
}

// ============================================================
// EVENT HANDLERS
// ============================================================

function handleToggleChange(e) {
    const toggle = e.target;
    const settingName = toggle.id || toggle.name;
    
    console.log(`Toggle changed: ${settingName} = ${toggle.checked}`);
    
    // Mostrar feedback visual
    showSettingFeedback(toggle.closest('.setting-item') || toggle.closest('.toggle-item'), toggle.checked);
}

function handlePaginationChange(e) {
    const btn = e.currentTarget;
    const container = btn.closest('.pagination-options');
    const currentActive = container.querySelector('.pagination-btn.active');
    
    // Remover clase active del botón anterior
    if (currentActive && currentActive !== btn) {
        currentActive.classList.remove('active');
    }
    
    // Agregar clase active al nuevo botón
    btn.classList.add('active');
    
    console.log(`Pagination changed: ${btn.textContent} items per page`);
}

function handleSelectChange(e) {
    const select = e.target;
    const settingName = select.id || select.name;
    
    console.log(`Select changed: ${settingName} = ${select.value}`);
    
    // Mostrar feedback visual
    showSettingFeedback(select.closest('.setting-group') || select.closest('.form-group'), true);
}

async function handleChangePassword(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const oldPassword = formData.get('old_password');
    const newPassword = formData.get('new_password');
    const confirmPassword = formData.get('confirm_password');
    
    // Validar
    if (!oldPassword || !newPassword || !confirmPassword) {
        showNotification('Por favor completa todos los campos', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showNotification('Las contraseñas no coinciden', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showNotification('La contraseña debe tener al menos 6 caracteres', 'error');
        return;
    }
    
    try {
        const token = getCsrfToken();
        const response = await fetch('/api/auth/change-password', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cambiar contraseña');
        }
        
        showNotification('Contraseña cambiada correctamente', 'success');
        form.reset();
        
    } catch (error) {
        console.error('Error changing password:', error);
        showNotification(error.message, 'error');
    }
}

function showSettingFeedback(element, isEnabled) {
    if (!element) return;
    
    // Agregar clase de feedback temporal
    element.classList.add('setting-changed');
    
    // Cambiar color temporalmente
    const originalBackground = element.style.backgroundColor;
    element.style.backgroundColor = isEnabled ? '#d4edda' : '#f8d7da';
    element.style.transition = 'background-color 0.3s';
    
    setTimeout(() => {
        element.classList.remove('setting-changed');
        element.style.backgroundColor = originalBackground;
    }, 1000);
}

async function saveAllSettings() {
    const saveBtn = document.querySelector('.btn-save-settings');
    if (!saveBtn) return;
    
    const originalText = saveBtn.innerHTML;
    
    // Mostrar estado de carga
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    saveBtn.disabled = true;
    
    try {
        // Recopilar todas las configuraciones
        const settings = collectAllSettings();
        
        // Guardar en el servidor
        const result = await updateBusinessSettings(settings);
        
        if (result.success) {
            showNotification('Configuraciones guardadas correctamente', 'success');
            
            // Mostrar éxito
            saveBtn.innerHTML = '<i class="fas fa-check"></i> Guardado';
            saveBtn.classList.add('btn-success');
            saveBtn.classList.remove('btn-primary');
            
            // Restaurar estado original después de 2 segundos
            setTimeout(() => {
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = false;
                saveBtn.classList.add('btn-primary');
                saveBtn.classList.remove('btn-success');
            }, 2000);
        } else {
            throw new Error(result.message || 'Error al guardar configuraciones');
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification(error.message, 'error');
        
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    }
}

function resetToDefaults() {
    if (confirm('¿Estás seguro de que quieres restaurar todas las configuraciones a sus valores predeterminados?')) {
        // Recargar configuraciones del servidor
        loadSettings();
        showNotification('Configuraciones restauradas', 'info');
    }
}

function editTemplate(e) {
    const btn = e.target.closest('.btn-edit-template');
    const templateItem = btn.closest('.template-item');
    const textElement = templateItem.querySelector('.template-text');
    const currentText = textElement.textContent;
    
    // Crear textarea para edición
    const textarea = document.createElement('textarea');
    textarea.className = 'form-control';
    textarea.value = currentText;
    textarea.rows = 3;
    
    // Reemplazar texto con textarea
    textElement.style.display = 'none';
    textElement.parentNode.insertBefore(textarea, textElement.nextSibling);
    
    // Cambiar botón a guardar
    btn.innerHTML = '<i class="fas fa-save"></i>';
    btn.classList.add('btn-save');
    btn.classList.remove('btn-edit-template');
    
    // Enfocar textarea
    textarea.focus();
    
    // Agregar event listener para guardar
    const saveHandler = function() {
        const newText = textarea.value.trim();
        
        if (newText) {
            textElement.textContent = newText;
            textElement.style.display = 'block';
            textarea.remove();
            
            // Restaurar botón
            btn.innerHTML = '<i class="fas fa-edit"></i>';
            btn.classList.remove('btn-save');
            btn.classList.add('btn-edit-template');
            
            // Remover event listener
            btn.removeEventListener('click', saveHandler);
            btn.addEventListener('click', editTemplate);
            
            showNotification('Plantilla actualizada', 'success');
            console.log('Template updated:', newText);
        }
    };
    
    btn.removeEventListener('click', editTemplate);
    btn.addEventListener('click', saveHandler);
}

// ============================================================
// COLLECT SETTINGS DATA
// ============================================================

function collectAllSettings() {
    const settings = {
        name: document.getElementById('business-name')?.value || '',
        business_type: document.getElementById('business-type')?.value || '',
        location: document.getElementById('location')?.value || '',
        opening_time: document.getElementById('open-time')?.value || '',
        closing_time: document.getElementById('close-time')?.value || '',
        delivery_enabled: document.getElementById('delivery-enabled')?.checked || false,
        delivery_radius_km: parseFloat(document.getElementById('delivery-radius')?.value) || 0,
        delivery_fee: parseFloat(document.getElementById('delivery-fee')?.value) || 0,
        notifications_enabled: document.getElementById('notifications-enabled')?.checked || false,
        whatsapp_enabled: document.getElementById('whatsapp-enabled')?.checked || false
    };
    
    // Recopilar otros toggles
    const toggles = document.querySelectorAll('.toggle input[type="checkbox"]');
    toggles.forEach(toggle => {
        const id = toggle.id || toggle.name;
        if (id && !settings.hasOwnProperty(id)) {
            settings[id] = toggle.checked;
        }
    });
    
    // Recopilar selects
    const selects = document.querySelectorAll('.form-select');
    selects.forEach(select => {
        const id = select.id || select.name;
        if (id && !settings.hasOwnProperty(id)) {
            settings[id] = select.value;
        }
    });
    
    return settings;
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function showLoadingState() {
    const container = document.querySelector('.settings-container');
    if (container) {
        container.style.opacity = '0.6';
        container.style.pointerEvents = 'none';
    }
}

function hideLoadingState() {
    const container = document.querySelector('.settings-container');
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