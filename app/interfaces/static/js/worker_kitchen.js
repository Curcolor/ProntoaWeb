/**
 * JavaScript para la interfaz de trabajadores de cocina.
 * Maneja la visualización y gestión de pedidos en cocina.
 */

let orders = [];

// Cargar pedidos al iniciar
document.addEventListener('DOMContentLoaded', function() {
    loadOrders();
    // Actualizar cada 30 segundos
    setInterval(loadOrders, 30000);
});

/**
 * Carga los pedidos desde el API
 */
async function loadOrders() {
    try {
        const response = await fetch('/api/orders/worker/kitchen');
        if (!response.ok) throw new Error('Error al cargar pedidos');
        
        const data = await response.json();
        orders = data.orders || [];
        renderOrders();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar pedidos', 'error');
    }
}

/**
 * Renderiza los pedidos en las columnas correspondientes
 */
function renderOrders() {
    // Limpiar columnas
    document.getElementById('received-orders').innerHTML = '';
    document.getElementById('preparing-orders').innerHTML = '';
    document.getElementById('ready-orders').innerHTML = '';
    
    // Filtrar y renderizar por estado
    const received = orders.filter(o => o.status === 'received');
    const preparing = orders.filter(o => o.status === 'preparing');
    const ready = orders.filter(o => o.status === 'ready');
    
    renderOrdersInColumn('received-orders', received, 'received');
    renderOrdersInColumn('preparing-orders', preparing, 'preparing');
    renderOrdersInColumn('ready-orders', ready, 'ready');
}

/**
 * Renderiza pedidos en una columna específica
 */
function renderOrdersInColumn(columnId, ordersList, status) {
    const column = document.getElementById(columnId);
    
    if (ordersList.length === 0) {
        column.innerHTML = '<p class="empty-message">No hay pedidos</p>';
        return;
    }
    
    ordersList.forEach(order => {
        const card = createOrderCard(order, status);
        column.appendChild(card);
    });
}

/**
 * Crea una tarjeta de pedido
 */
function createOrderCard(order, status) {
    const template = document.getElementById('order-card-template');
    const card = template.content.cloneNode(true);
    
    // Establecer datos
    card.querySelector('.order-card').dataset.orderId = order.id;
    card.querySelector('.order-id').textContent = order.id;
    card.querySelector('.order-time').textContent = formatTime(order.created_at);
    card.querySelector('.customer-name').textContent = order.customer_name || 'Cliente';
    
    // Items del pedido
    const itemsContainer = card.querySelector('.order-items');
    itemsContainer.innerHTML = order.items.map(item => `
        <div class="order-item">
            <span>${item.quantity}x ${item.product_name}</span>
            <span>$${item.subtotal.toFixed(0)}</span>
        </div>
    `).join('');
    
    // Notas
    const notesElement = card.querySelector('.delivery-notes');
    if (order.delivery_notes) {
        notesElement.textContent = `Nota: ${order.delivery_notes}`;
    } else {
        notesElement.parentElement.style.display = 'none';
    }
    
    // Botones según estado
    const actionsContainer = card.querySelector('.order-actions');
    actionsContainer.innerHTML = getActionButtons(order.id, status);
    
    return card;
}

/**
 * Obtiene los botones de acción según el estado
 */
function getActionButtons(orderId, status) {
    switch(status) {
        case 'received':
            return `
                <button class="btn-action btn-start" onclick="startPreparing(${orderId})">
                    👨‍🍳 Empezar a Preparar
                </button>
            `;
        case 'preparing':
            return `
                <button class="btn-action btn-ready" onclick="markAsReady(${orderId})">
                    ✅ Marcar como Listo
                </button>
            `;
        case 'ready':
            return `
                <div style="text-align: center; color: #4CAF50;">
                    <strong>✓ Listo para enviar</strong>
                </div>
            `;
        default:
            return '';
    }
}

/**
 * Inicia la preparación de un pedido
 */
async function startPreparing(orderId) {
    if (!confirm('¿Empezar a preparar este pedido?')) return;
    
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            credentials: 'include',
            body: JSON.stringify({
                status: 'preparing'
            })
        });
        
        if (!response.ok) throw new Error('Error al actualizar estado');
        
        showNotification('Pedido en preparación', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al actualizar pedido', 'error');
    }
}

/**
 * Marca un pedido como listo
 */
async function markAsReady(orderId) {
    if (!confirm('¿Marcar este pedido como listo?')) return;
    
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            credentials: 'include',
            body: JSON.stringify({
                status: 'ready'
            })
        });
        
        if (!response.ok) throw new Error('Error al actualizar estado');
        
        showNotification('Pedido listo para enviar', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al actualizar pedido', 'error');
    }
}

/**
 * Formatea la hora
 */
function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 60000); // minutos
    
    if (diff < 1) return 'Ahora';
    if (diff < 60) return `Hace ${diff} min`;
    
    return date.toLocaleTimeString('es-CO', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

/**
 * Muestra una notificación
 */
function showNotification(message, type = 'info') {
    // Aquí puedes implementar tu sistema de notificaciones
    alert(message);
}
