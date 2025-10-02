// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth page loaded');
    
    // Inicializar validación de formularios
    initializeFormValidation();
    
    // Configurar toggle de contraseña
    setupPasswordToggle();
});

function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        
        // Validación en tiempo real
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', validateInput);
            input.addEventListener('input', clearValidationState);
        });
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.btn-auth');
    const isValid = validateForm(form);
    
    if (isValid) {
        // Mostrar estado de carga
        showLoadingState(submitBtn);
        
        // Simular envío del formulario
        setTimeout(() => {
            hideLoadingState(submitBtn);
            
            // Aquí se implementaría el envío real al servidor
            console.log('Formulario enviado:', new FormData(form));
            
            // Redirigir según el tipo de formulario
            if (form.closest('[data-page="login"]') || form.action.includes('login')) {
                window.location.href = '/dashboard';
            } else if (form.closest('[data-page="register"]') || form.action.includes('register')) {
                window.location.href = '/dashboard';
            }
        }, 2000);
    }
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('.form-control[required]');
    
    inputs.forEach(input => {
        if (!validateInput({ target: input })) {
            isValid = false;
        }
    });
    
    // Validación especial para confirmación de contraseña
    const password = form.querySelector('#password');
    const confirmPassword = form.querySelector('#confirmPassword');
    
    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            showValidationError(confirmPassword, 'Las contraseñas no coinciden');
            isValid = false;
        }
    }
    
    return isValid;
}

function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Limpiar estado anterior
    clearValidationState({ target: input });
    
    // Validación de campo requerido
    if (input.hasAttribute('required') && !value) {
        errorMessage = 'Este campo es requerido';
        isValid = false;
    }
    
    // Validaciones específicas por tipo
    if (value && isValid) {
        switch (input.type) {
            case 'email':
                if (!isValidEmail(value)) {
                    errorMessage = 'Ingresa un email válido';
                    isValid = false;
                }
                break;
            case 'password':
                if (input.id === 'password' && !isValidPassword(value)) {
                    errorMessage = 'La contraseña debe tener al menos 8 caracteres, una mayúscula y un número';
                    isValid = false;
                }
                break;
            case 'tel':
                if (!isValidPhone(value)) {
                    errorMessage = 'Ingresa un número de teléfono válido';
                    isValid = false;
                }
                break;
        }
    }
    
    if (isValid) {
        showValidationSuccess(input);
    } else {
        showValidationError(input, errorMessage);
    }
    
    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPassword(password) {
    // Al menos 8 caracteres, una mayúscula y un número
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
}

function isValidPhone(phone) {
    // Formato básico para números colombianos
    const phoneRegex = /^(\+57\s?)?[3][0-9]{9}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

function showValidationError(input, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    
    // Buscar o crear elemento de error
    let errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        input.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

function showValidationSuccess(input) {
    input.classList.add('is-valid');
    input.classList.remove('is-invalid');
    
    // Remover mensaje de error si existe
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function clearValidationState(e) {
    const input = e.target;
    input.classList.remove('is-valid', 'is-invalid');
    
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function setupPasswordToggle() {
    const toggleBtns = document.querySelectorAll('.password-toggle');
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentNode.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
                this.classList.add('active');
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
                this.classList.remove('active');
            }
        });
    });
}

function showLoadingState(button) {
    button.classList.add('loading');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
}

function hideLoadingState(button) {
    button.classList.remove('loading');
    button.disabled = false;
    
    // Restaurar texto original
    const isLogin = button.closest('form').action.includes('login');
    if (isLogin) {
        button.innerHTML = '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
    } else {
        button.innerHTML = '<i class="fas fa-user-plus"></i> Crear Cuenta';
    }
}

// Función global para toggle de contraseña (llamada desde HTML)
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentNode.querySelector('.password-toggle');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
        button.classList.add('active');
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
        button.classList.remove('active');
    }
}