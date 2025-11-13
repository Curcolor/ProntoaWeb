/**
 * JavaScript para la interfaz de repartidores.
 * Maneja la visualización y gestión de entregas.
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
        const response = await fetch('/api/orders/worker/delivery');
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
    document.getElementById('ready-orders').innerHTML = '';
    document.getElementById('sent-orders').innerHTML = '';
    document.getElementById('paid-orders').innerHTML = '';
    
    // Filtrar y renderizar por estado
    const ready = orders.filter(o => o.status === 'ready');
    const sent = orders.filter(o => o.status === 'sent');
    const paid = orders.filter(o => o.status === 'paid');
    
    renderOrdersInColumn('ready-orders', ready, 'ready');
    renderOrdersInColumn('sent-orders', sent, 'sent');
    renderOrdersInColumn('paid-orders', paid, 'paid');
}

/**
 * Renderiza pedidos en una columna específica
 */
function renderOrdersInColumn(columnId, ordersList, status) {
    const column = document.getElementById(columnId);
    
    if (ordersList.length === 0) {
        const emptyMsg = status === 'paid' ? 
            'No hay pedidos entregados hoy' : 
            'No hay pedidos';
        column.innerHTML = `<p class="empty-message">${emptyMsg}</p>`;
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
    
    // Dirección
    card.querySelector('.address-text').textContent = 
        order.delivery_address || 'Dirección no especificada';
    
    // Teléfono
    const phoneElement = card.querySelector('.phone-number');
    phoneElement.textContent = order.customer_phone || 'N/A';
    phoneElement.dataset.phone = order.customer_phone;
    
    // Total
    card.querySelector('.total-amount').textContent = 
        order.total_amount.toFixed(0);
    
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
        case 'ready':
            return `
                <button class="btn-action btn-pickup" onclick="pickupOrder(${orderId})">
                    🚴 Recoger Pedido
                </button>
            `;
        case 'sent':
            return `
                <button class="btn-action btn-delivered" onclick="markAsDelivered(${orderId})">
                    ✅ Marcar como Entregado
                </button>
            `;
        case 'paid':
            return `
                <div style="text-align: center; color: #4CAF50;">
                    <strong>✓ Entregado</strong>
                </div>
            `;
        default:
            return '';
    }
}

/**
 * Recoge un pedido para entrega
 */
async function pickupOrder(orderId) {
    if (!confirm('¿Recoger este pedido para entrega?')) return;
    
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
                status: 'sent'
            })
        });
        
        if (!response.ok) throw new Error('Error al actualizar estado');
        
        showNotification('Pedido recogido. ¡Buen viaje!', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al actualizar pedido', 'error');
    }
}

/**
 * Marca un pedido como entregado
 */
async function markAsDelivered(orderId) {
    if (!confirm('¿Confirmar que el pedido fue entregado?')) return;
    
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
                status: 'paid'
            })
        });
        
        if (!response.ok) throw new Error('Error al actualizar estado');
        
        showNotification('¡Pedido entregado exitosamente!', 'success');
        loadOrders();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al actualizar pedido', 'error');
    }
}

/**
 * Llama al cliente
 */
function callCustomer(button) {
    const card = button.closest('.order-card');
    const phone = card.querySelector('.phone-number').dataset.phone;
    
    if (phone && phone !== 'N/A') {
        window.location.href = `tel:${phone}`;
    } else {
        showNotification('Teléfono no disponible', 'warning');
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
