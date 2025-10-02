// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Inicializar tooltips si se necesitan
    initializeTooltips();
    
    // Configurar drag and drop para las tarjetas del Kanban
    initializeKanbanDragDrop();
    
    // Actualizar métricas en tiempo real (simulado)
    updateMetricsRealTime();
});

function initializeTooltips() {
    // Inicializar tooltips de Bootstrap si están disponibles
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function initializeKanbanDragDrop() {
    const orderCards = document.querySelectorAll('.order-card');
    const columns = document.querySelectorAll('.kanban-column');
    
    orderCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        card.draggable = true;
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
    });
}

function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.innerHTML);
    e.target.style.opacity = '0.5';
}

function handleDragEnd(e) {
    e.target.style.opacity = '1';
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    // Aquí se implementaría la lógica para mover la tarjeta
    console.log('Card dropped in:', e.currentTarget);
}

function updateMetricsRealTime() {
    // Simular actualizaciones en tiempo real
    setInterval(() => {
        const statusIndicator = document.querySelector('.status-indicator');
        const lastUpdate = document.querySelector('.last-update');
        
        if (lastUpdate) {
            lastUpdate.textContent = 'Última actualización: hace ' + Math.floor(Math.random() * 5 + 1) + ' min';
        }
    }, 30000); // Actualizar cada 30 segundos
}

// Función para actualizar el conteo de pedidos en las columnas
function updateColumnCounts() {
    const columns = document.querySelectorAll('.kanban-column');
    
    columns.forEach(column => {
        const cards = column.querySelectorAll('.order-card');
        const header = column.querySelector('.column-header h3');
        const currentText = header.textContent;
        const newText = currentText.replace(/\(\d+\)/, `(${cards.length})`);
        header.textContent = newText;
    });
}

// Función para mostrar detalles de un pedido
function showOrderDetails(orderId) {
    // Aquí se implementaría un modal con los detalles del pedido
    console.log('Mostrar detalles del pedido:', orderId);
}

// Event listeners para las tarjetas de pedidos
document.addEventListener('click', function(e) {
    if (e.target.closest('.order-card')) {
        const orderCard = e.target.closest('.order-card');
        const orderId = orderCard.querySelector('.order-id').textContent;
        showOrderDetails(orderId);
    }
});