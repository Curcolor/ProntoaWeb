/**
 * auth.js - Autenticación unificada (User y Worker)
 * Detecta el tipo de usuario y redirige al dashboard correspondiente
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('🔐 Auth JS cargado');
  
  // Toggle mostrar/ocultar contraseña
  setupPasswordToggle();
  
  // Manejar formulario de login
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  
  // Manejar formulario de registro
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }
});

// ==================== LOGIN ====================

async function handleLogin(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const remember = document.getElementById('remember')?.checked || false;
  
  // Mostrar loading
  showLoading(true);
  clearErrors();
  
  try {
    const token = getCsrfToken();
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token
      },
      credentials: 'include',
      body: JSON.stringify({ email, password, remember })
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      console.log('✅ Login exitoso:', data.user_type);
      
      // Guardar info en localStorage
      localStorage.setItem('prontoa_user', JSON.stringify(data.user));
      localStorage.setItem('prontoa_user_type', data.user_type);
      
      // Redirigir según tipo de usuario
      if (data.user_type === 'worker') {
        window.location.href = '/worker-orders';
      } else {
        window.location.href = '/dashboard';
      }
    } else {
      showError(data.message || 'Error al iniciar sesión');
    }
  } catch (error) {
    console.error('Error en login:', error);
    showError('Error de conexión. Por favor intenta de nuevo.');
  } finally {
    showLoading(false);
  }
}

// ==================== REGISTRO ====================

async function handleRegister(e) {
  e.preventDefault();
  
  const formData = {
    email: document.getElementById('email').value,
    password: document.getElementById('password').value,
    confirm_password: document.getElementById('confirmPassword').value,
    full_name: document.getElementById('fullName').value,
    phone: document.getElementById('phone').value,
    business_name: document.getElementById('businessName').value,
    business_type: document.getElementById('businessType').value
  };
  
  // Validación de contraseñas
  if (formData.password !== formData.confirm_password) {
    showError('Las contraseñas no coinciden');
    return;
  }
  
  showLoading(true);
  clearErrors();
  
  try {
    const token = getCsrfToken();
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token
      },
      credentials: 'include',
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      showSuccess('Registro exitoso. Redirigiendo al login...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } else {
      showError(data.message || 'Error en el registro');
    }
  } catch (error) {
    console.error('Error en registro:', error);
    showError('Error de conexión. Por favor intenta de nuevo.');
  } finally {
    showLoading(false);
  }
}

// ==================== LOGOUT ====================

async function logout() {
  try {
    const token = getCsrfToken();
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-Token': token
      }
    });
    
    // Limpiar localStorage
    localStorage.removeItem('prontoa_user');
    localStorage.removeItem('prontoa_user_type');
    
    // Redirigir al login
    window.location.href = '/login';
  } catch (error) {
    console.error('Error en logout:', error);
    window.location.href = '/login';
  }
}

// ==================== UTILIDADES ====================

function setupPasswordToggle() {
  document.querySelectorAll('.password-toggle').forEach(btn => {
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

function showLoading(show) {
  const submitBtn = document.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = show;
    submitBtn.textContent = show ? 'Cargando...' : submitBtn.dataset.originalText || 'Iniciar Sesión';
    if (!submitBtn.dataset.originalText) {
      submitBtn.dataset.originalText = submitBtn.textContent;
    }
  }
}

function showError(message) {
  const errorDiv = document.querySelector('.error-message') || createMessageDiv('error');
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
}

function showSuccess(message) {
  const successDiv = document.querySelector('.success-message') || createMessageDiv('success');
  successDiv.textContent = message;
  successDiv.style.display = 'block';
}

function clearErrors() {
  const errorDiv = document.querySelector('.error-message');
  const successDiv = document.querySelector('.success-message');
  if (errorDiv) errorDiv.style.display = 'none';
  if (successDiv) successDiv.style.display = 'none';
}

function createMessageDiv(type) {
  const div = document.createElement('div');
  div.className = `${type}-message`;
  div.style.padding = '12px';
  div.style.marginBottom = '16px';
  div.style.borderRadius = '8px';
  div.style.display = 'none';
  
  if (type === 'error') {
    div.style.backgroundColor = '#fee';
    div.style.color = '#c33';
    div.style.border = '1px solid #fcc';
  } else {
    div.style.backgroundColor = '#efe';
    div.style.color = '#3c3';
    div.style.border = '1px solid #cfc';
  }
  
  const form = document.querySelector('form');
  if (form) {
    form.insertBefore(div, form.firstChild);
  }
  
  return div;
}

// Exportar para uso global
window.logout = logout;
