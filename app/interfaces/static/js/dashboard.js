// dashboard.js - Dashboard Kanban simplificado

document.addEventListener('DOMContentLoaded', () => {
  console.log('✓ Dashboard cargado');
  
  // Actualizar timestamp de última actualización cada 30s
  const lastUpdate = document.querySelector('.last-update');
  if (lastUpdate) {
    setInterval(() => {
      const min = Math.floor(Math.random() * 5 + 1);
      lastUpdate.textContent = `Última actualización: hace ${min} min`;
    }, 30000);
  }
  
  // Hacer tarjetas arrastrables (Kanban)
  makeKanbanDraggable();
});

// Función para habilitar drag & drop en tarjetas Kanban
function makeKanbanDraggable() {
  const cards = document.querySelectorAll('.order-card');
  const columns = document.querySelectorAll('.kanban-column');
  
  cards.forEach(card => {
    card.draggable = true;
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.effectAllowed = 'move';
      card.style.opacity = '0.5';
    });
    card.addEventListener('dragend', () => {
      card.style.opacity = '1';
    });
  });
  
  columns.forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.classList.add('drag-over');
    });
    col.addEventListener('dragleave', () => {
      col.classList.remove('drag-over');
    });
    col.addEventListener('drop', (e) => {
      e.preventDefault();
      col.classList.remove('drag-over');
      console.log('Tarjeta movida a:', col.querySelector('.column-header h3').textContent);
    });
  });
}

// Click en tarjeta: mostrar ID en consola
document.addEventListener('click', (e) => {
  const card = e.target.closest('.order-card');
  if (card) {
    const id = card.querySelector('.order-id')?.textContent || 'desconocido';
    console.log('Pedido seleccionado:', id);
  }
});