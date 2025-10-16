// auth.js - Autenticación simplificada

/**
 * Detecta si estamos en modo desarrollo usando la configuración de Flask
 * @returns {boolean} true si DEBUG está habilitado en Flask
 */
function isDevelopmentMode() {
  // Usar la configuración que pasa Flask desde base.html
  return window.appConfig && window.appConfig.debug === true;
}

/**
 * Muestra credenciales de demo solo en desarrollo
 */
function showDemoCredentials() {
  if (!isDevelopmentMode()) {
    console.log('🔒 Modo Producción: Credenciales no mostradas');
    return;
  }

  // Mostrar en página (solo desarrollo)
  const subtitle = document.querySelector('.auth-subtitle');
  if (subtitle) {
    const hint = document.createElement('div');
    hint.style.marginTop = '1rem';
    hint.style.fontSize = '0.85rem';
    hint.style.color = '#666';
    hint.style.backgroundColor = '#f0f0f0';
    hint.style.padding = '0.75rem';
    hint.style.borderRadius = '4px';
    hint.style.border = '1px solid #ddd';
    hint.innerHTML = `
      <strong>🔧 Modo Desarrollo (DEBUG=True) - Credenciales Demo:</strong><br>
      <small style="color: #0099ff;"><strong>Admin:</strong> admin@prontoa.test / AdminPass123</small><br>
      <small style="color: #ff00ff;"><strong>Worker:</strong> worker@prontoa.test / WorkerPass123</small>
    `;
    subtitle.parentNode.insertBefore(hint, subtitle.nextSibling);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  
  // Toggle simple: mostrar/ocultar contraseña
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

  // Mostrar credenciales demo solo en desarrollo
  showDemoCredentials();
});