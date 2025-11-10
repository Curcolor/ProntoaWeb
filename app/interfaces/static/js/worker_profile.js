// worker_profile.js - Funcionalidad del perfil del trabajador

document.addEventListener('DOMContentLoaded', () => {
  console.log('✓ Worker profile cargado');

  // Agregar event listeners a botones de acción
  document.querySelectorAll('.action-btn').forEach((btn) => {
    btn.addEventListener('click', handleActionClick);
  });
});

function handleActionClick(e) {
  const button = e.currentTarget;
  const action = button.textContent.trim().split('\n')[1]; // Obtener el texto

  console.log('Acción clickeada:', action);

  if (action.includes('Cerrar Sesión')) {
    // Redirigir a logout
    window.location.href = '/logout';
  } else if (action.includes('Editar')) {
    showNotification('Edición de perfil - Próximamente', 'info');
  } else if (action.includes('Cambiar')) {
    showNotification('Cambio de contraseña - Próximamente', 'info');
  } else if (action.includes('Notificaciones')) {
    showNotification('Configuración de notificaciones - Próximamente', 'info');
  }
}

function showNotification(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
  toast.style.zIndex = '9999';
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
}
