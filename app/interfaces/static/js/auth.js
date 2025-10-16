// auth.js - Autenticación simplificada

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

  // Mostrar credenciales demo en la página
  const subtitle = document.querySelector('.auth-subtitle');
  if (subtitle) {
    const hint = document.createElement('div');
    hint.style.marginTop = '1rem';
    hint.style.fontSize = '0.85rem';
    hint.style.color = '#666';
    hint.innerHTML = `
      <strong>Demo:</strong><br>
      admin@prontoa.test / AdminPass123<br>
      worker@prontoa.test / WorkerPass123
    `;
    subtitle.parentNode.insertBefore(hint, subtitle.nextSibling);
  }

  console.log('✓ Auth JS cargado');
});

// Función global para toggle desde HTML
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  input.type = input.type === 'password' ? 'text' : 'password';
  const btn = input.parentNode.querySelector('.password-toggle');
  if (btn) btn.classList.toggle('active');
}