// main.js - Utilidades globales simplificadas

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 ProntoaWeb cargado');
  
  // Agregar animaciones de fade-in a elementos principales
  document.querySelectorAll('.card, .alert, main > *').forEach((el, i) => {
    setTimeout(() => el.classList.add('fade-in'), i * 100);
  });
});

// Objeto global para API (simplificado)
window.API = {
  baseURL: '/api',
  
  async get(endpoint) {
    const res = await fetch(`${this.baseURL}${endpoint}`);
    return res.json();
  },
  
  async post(endpoint, data) {
    const res = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  }
};

// Utilidad: mostrar notificación toast
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
  toast.style.zIndex = '9999';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.remove(), 3000);
}

// Utilidad: formatear fecha en español
function formatDate(date) {
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

// Exportar utilidades globales
window.ProntoaWeb = { showToast, formatDate, API: window.API };