// Settings JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page loaded');
    
    // Inicializar configuraciones
    initializeSettings();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar configuraciones guardadas
    loadSavedSettings();
});

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
    const saveBtn = document.querySelector('.btn-primary');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAllSettings);
    }
    
    // Botón de restaurar valores
    const resetBtn = document.querySelector('.btn-secondary');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetToDefaults);
    }
    
    // Botón de editar plantilla
    const editBtns = document.querySelectorAll('.btn-edit');
    editBtns.forEach(btn => {
        btn.addEventListener('click', editTemplate);
    });
}

function handleToggleChange(e) {
    const toggle = e.target;
    const settingName = toggle.closest('.toggle-item').querySelector('span').textContent;
    
    console.log(`Toggle changed: ${settingName} = ${toggle.checked}`);
    
    // Mostrar feedback visual
    showSettingFeedback(toggle.closest('.toggle-item'), toggle.checked);
    
    // Guardar en localStorage temporalmente
    const settings = getLocalSettings();
    settings.toggles = settings.toggles || {};
    settings.toggles[settingName] = toggle.checked;
    saveLocalSettings(settings);
}

function handlePaginationChange(e) {
    const btn = e.target;
    const container = btn.closest('.pagination-options');
    const currentActive = container.querySelector('.pagination-btn.active');
    
    // Remover clase active del botón anterior
    if (currentActive) {
        currentActive.classList.remove('active');
    }
    
    // Agregar clase active al nuevo botón
    btn.classList.add('active');
    
    console.log(`Pagination changed: ${btn.textContent} items per page`);
    
    // Guardar configuración
    const settings = getLocalSettings();
    settings.pagination = btn.textContent;
    saveLocalSettings(settings);
}

function handleSelectChange(e) {
    const select = e.target;
    const settingName = select.id || select.name;
    
    console.log(`Select changed: ${settingName} = ${select.value}`);
    
    // Mostrar feedback visual
    showSettingFeedback(select.closest('.setting-group'), true);
    
    // Guardar configuración
    const settings = getLocalSettings();
    settings.selects = settings.selects || {};
    settings.selects[settingName] = select.value;
    saveLocalSettings(settings);
}

function showSettingFeedback(element, isEnabled) {
    // Agregar clase de feedback temporal
    element.classList.add('setting-changed');
    
    // Cambiar color temporalmente
    const originalBackground = element.style.backgroundColor;
    element.style.backgroundColor = isEnabled ? '#d4edda' : '#f8d7da';
    
    setTimeout(() => {
        element.classList.remove('setting-changed');
        element.style.backgroundColor = originalBackground;
    }, 1000);
}

function saveAllSettings() {
    const saveBtn = document.querySelector('.btn-primary');
    const originalText = saveBtn.innerHTML;
    
    // Mostrar estado de carga
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    saveBtn.disabled = true;
    
    // Recopilar todas las configuraciones
    const settings = collectAllSettings();
    
    // Simular guardado en servidor
    setTimeout(() => {
        console.log('Settings saved:', settings);
        
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
        
        // Guardar en localStorage
        saveLocalSettings(settings);
        
    }, 1500);
}

function resetToDefaults() {
    if (confirm('¿Estás seguro de que quieres restaurar todas las configuraciones a sus valores predeterminados?')) {
        // Limpiar localStorage
        localStorage.removeItem('prontoaSettings');
        
        // Recargar página para aplicar defaults
        window.location.reload();
    }
}

function editTemplate(e) {
    const btn = e.target.closest('.btn-edit');
    const templateItem = btn.closest('.template-item');
    const textElement = templateItem.querySelector('p');
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
    
    // Enfocar textarea
    textarea.focus();
    
    // Agregar event listener para guardar
    btn.addEventListener('click', function saveTemplate() {
        const newText = textarea.value.trim();
        
        if (newText) {
            textElement.textContent = newText;
            textElement.style.display = 'block';
            textarea.remove();
            
            // Restaurar botón
            btn.innerHTML = '<i class="fas fa-edit"></i>';
            btn.classList.remove('btn-save');
            
            // Remover event listener
            btn.removeEventListener('click', saveTemplate);
            
            console.log('Template updated:', newText);
        }
    });
}

function collectAllSettings() {
    const settings = {
        toggles: {},
        selects: {},
        pagination: document.querySelector('.pagination-btn.active')?.textContent || '10',
        timeSettings: {
            openTime: document.querySelector('input[type="time"]:first-of-type')?.value || '08:00',
            closeTime: document.querySelector('input[type="time"]:last-of-type')?.value || '20:00'
        }
    };
    
    // Recopilar toggles
    document.querySelectorAll('.toggle input[type="checkbox"]').forEach(toggle => {
        const label = toggle.closest('.toggle-item').querySelector('span').textContent;
        settings.toggles[label] = toggle.checked;
    });
    
    // Recopilar selects
    document.querySelectorAll('.form-select').forEach(select => {
        const name = select.id || select.name;
        if (name) {
            settings.selects[name] = select.value;
        }
    });
    
    return settings;
}

function loadSavedSettings() {
    const settings = getLocalSettings();
    
    if (settings) {
        // Aplicar toggles guardados
        if (settings.toggles) {
            Object.entries(settings.toggles).forEach(([label, checked]) => {
                const toggle = Array.from(document.querySelectorAll('.toggle-item')).find(item => 
                    item.querySelector('span').textContent === label
                )?.querySelector('input[type="checkbox"]');
                
                if (toggle) {
                    toggle.checked = checked;
                }
            });
        }
        
        // Aplicar selects guardados
        if (settings.selects) {
            Object.entries(settings.selects).forEach(([name, value]) => {
                const select = document.getElementById(name) || document.querySelector(`[name="${name}"]`);
                if (select) {
                    select.value = value;
                }
            });
        }
        
        // Aplicar paginación guardada
        if (settings.pagination) {
            const paginationBtn = Array.from(document.querySelectorAll('.pagination-btn')).find(btn => 
                btn.textContent === settings.pagination
            );
            if (paginationBtn) {
                document.querySelector('.pagination-btn.active')?.classList.remove('active');
                paginationBtn.classList.add('active');
            }
        }
        
        // Aplicar configuraciones de tiempo
        if (settings.timeSettings) {
            const openTimeInput = document.querySelector('input[type="time"]:first-of-type');
            const closeTimeInput = document.querySelector('input[type="time"]:last-of-type');
            
            if (openTimeInput) openTimeInput.value = settings.timeSettings.openTime;
            if (closeTimeInput) closeTimeInput.value = settings.timeSettings.closeTime;
        }
    }
}

function getLocalSettings() {
    try {
        return JSON.parse(localStorage.getItem('prontoaSettings')) || {};
    } catch (e) {
        return {};
    }
}

function saveLocalSettings(settings) {
    try {
        localStorage.setItem('prontoaSettings', JSON.stringify(settings));
    } catch (e) {
        console.error('Error saving settings to localStorage:', e);
    }
}