/**
 * worker.js - Dashboard del trabajador con tipos (planta y repartidor)
 */

// Variables globales
let workerData = null;
let workerType = null;
let refreshInterval = null;
const REFRESH_INTERVAL_MS = 15000;

// Inicializacion
document.addEventListener('DOMContentLoaded', function() {
    console.log('Worker Dashboard cargado');
    loadWorkerFromStorage();
    if (!workerData) {
        window.location.href = '/login';
        return;
    }
    workerType = workerData.worker_type || 'planta';
    console.log('Tipo de trabajador:', workerType);
    updateWorkerTypeUI();
    loadWorkerOrders();
    startAutoRefresh();
    setupEventListeners();
});

// Actualizar UI segun tipo
function updateWorkerTypeUI() {
    const workerRoleEl = document.getElementById('worker-role');
    if (workerRoleEl) {
        if (workerType === 'planta') {
            workerRoleEl.innerHTML = '<i class="fas fa-utensils"></i> Trabajador en Planta';
        } else {
            workerRoleEl.innerHTML = '<i class="fas fa-motorcycle"></i> Repartidor';
        }
    }
    const pageTitle = document.querySelector('.worker-top-bar h1');
    if (pageTitle) {
        if (workerType === 'planta') {
            pageTitle.innerHTML = '<i class="fas fa-fire"></i> Pedidos para Preparar';
        } else {
            pageTitle.innerHTML = '<i class="fas fa-truck"></i> Pedidos para Entregar';
        }
    }
}

// Cargar pedidos
async function loadWorkerOrders() {
    try {
        let statusToLoad = workerType === 'planta' ? ['received', 'preparing'] : ['ready', 'sent'];
        const allOrders = [];
        for (const status of statusToLoad) {
            const response = await fetch(`/api/orders?status=${status}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            const data = await response.json();
            if (response.ok && data.orders) {
                allOrders.push(...data.orders);
            }
        }
        renderWorkerKanban(allOrders);
        updateLastRefreshTime();
    } catch (error) {
        console.error('Error cargando pedidos:', error);
        showNotification('Error al cargar pedidos', 'error');
    }
}

// Renderizar Kanban
function renderWorkerKanban(orders) {
    const container = document.getElementById('worker-orders-container');
    if (!container) return;
    if (!orders || orders.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle fa-3x" style="color: #25D366;"></i>
                <h3>Todo listo!</h3>
                <p>No hay pedidos pendientes en este momento</p>
            </div>
        `;
        return;
    }
    const ordersByStatus = {};
    orders.forEach(order => {
        if (!ordersByStatus[order.status]) ordersByStatus[order.status] = [];
        ordersByStatus[order.status].push(order);
    });
    let html = '<div class="kanban-board">';
    if (workerType === 'planta') {
        html += createKanbanColumn('received', 'Recibidos', ordersByStatus.received || [], '#17a2b8');
        html += createKanbanColumn('preparing', 'En Preparacion', ordersByStatus.preparing || [], '#ffc107');
    } else {
        html += createKanbanColumn('ready', 'Listos', ordersByStatus.ready || [], '#28a745');
        html += createKanbanColumn('sent', 'En Camino', ordersByStatus.sent || [], '#007bff');
    }
    html += '</div>';
    container.innerHTML = html;
    addOrderCardListeners();
}

// Crear columna Kanban
function createKanbanColumn(status, title, orders, color) {
    let html = `<div class="kanban-column" data-status="${status}">
        <div class="kanban-column-header" style="border-left: 4px solid ${color};">
            <h3>${title}</h3>
            <span class="kanban-count">${orders.length}</span>
        </div>
        <div class="kanban-column-content">`;
    if (orders.length === 0) {
        html += '<div class="kanban-empty"><i class="fas fa-inbox"></i><p>No hay pedidos</p></div>';
    } else {
        orders.forEach(order => { html += createOrderCard(order); });
    }
    html += '</div></div>';
    return html;
}

// Crear card de pedido
function createOrderCard(order) {
    const customerName = order.customer?.name || 'Cliente';
    const timeAgo = getTimeAgo(order.created_at);
    const itemsHTML = order.items?.map(item => `<div class="order-item"><span class="item-quantity">${item.quantity}x</span><span class="item-name">${item.product_name}</span></div>`).join('') || '';
    const actionsHTML = getOrderActions(order);
    return `<div class="worker-order-card" data-order-id="${order.id}">
        <div class="order-header">
            <div class="order-number"><i class="fas fa-receipt"></i> #${order.order_number}</div>
            ${getStatusBadge(order.status)}
        </div>
        <div class="order-customer"><i class="fas fa-user"></i><div class="customer-info"><strong>${customerName}</strong></div></div>
        <div class="order-items-list"><strong>Productos:</strong>${itemsHTML}</div>
        <div class="order-meta"><span class="order-time"><i class="fas fa-clock"></i> ${timeAgo}</span></div>
        <div class="order-actions">${actionsHTML}</div>
    </div>`;
}

// Obtener acciones del pedido
function getOrderActions(order) {
    const id = order.id;
    const num = order.order_number;
    if (workerType === 'planta') {
        if (order.status === 'received') {
            return `<button class="btn btn-primary btn-accept" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-check"></i> Aceptar</button>`;
        } else if (order.status === 'preparing') {
            return `<button class="btn btn-success btn-mark-ready" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-check-double"></i> Marcar Listo</button>
            <button class="btn btn-secondary btn-cancel" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-undo"></i> Cancelar</button>`;
        }
    }
    if (workerType === 'repartidor') {
        if (order.status === 'ready') {
            return `<button class="btn btn-primary btn-accept-delivery" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-motorcycle"></i> Aceptar Entrega</button>`;
        } else if (order.status === 'sent') {
            return `<button class="btn btn-success btn-mark-paid" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-dollar-sign"></i> Marcar Pagado</button>
            <button class="btn btn-secondary btn-cancel" data-order-id="${id}" data-order-number="${num}"><i class="fas fa-undo"></i> Cancelar</button>`;
        }
    }
    return '';
}

// Obtener badge de estado
function getStatusBadge(status) {
    const badges = {
        'received': '<span class="badge badge-info"><i class="fas fa-inbox"></i> Recibido</span>',
        'preparing': '<span class="badge badge-warning"><i class="fas fa-fire"></i> Preparando</span>',
        'ready': '<span class="badge badge-success"><i class="fas fa-check-circle"></i> Listo</span>',
        'sent': '<span class="badge badge-primary"><i class="fas fa-shipping-fast"></i> Enviado</span>'
    };
    return badges[status] || `<span class="badge badge-secondary">${status}</span>`;
}

// Acciones de pedidos
async function acceptOrder(orderId, orderNumber) {
    if (!confirm(`Aceptar pedido #${orderNumber} para preparacion?`)) return;
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/accept-to-preparing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message);
        showNotification(`Pedido #${orderNumber} aceptado!`, 'success');
        setTimeout(() => loadWorkerOrders(), 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function markOrderReady(orderId, orderNumber) {
    if (!confirm(`Confirmar que el pedido #${orderNumber} esta listo?`)) return;
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/mark-ready`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message);
        showNotification(`Pedido #${orderNumber} marcado como listo!`, 'success');
        if (data.notification_sent) showNotification('Cliente notificado por WhatsApp', 'info');
        setTimeout(() => loadWorkerOrders(), 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function acceptDelivery(orderId, orderNumber) {
    if (!confirm(`Aceptar pedido #${orderNumber} para entrega?`)) return;
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/accept-to-sent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message);
        showNotification(`Entrega #${orderNumber} aceptada!`, 'success');
        setTimeout(() => loadWorkerOrders(), 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function markOrderPaid(orderId, orderNumber) {
    if (!confirm(`Confirmar que el pedido #${orderNumber} fue pagado?`)) return;
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/mark-paid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message);
        showNotification(`Pedido #${orderNumber} pagado y cerrado!`, 'success');
        setTimeout(() => loadWorkerOrders(), 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function cancelOrder(orderId, orderNumber) {
    if (!confirm(`Cancelar pedido #${orderNumber}? Volvera al estado anterior.`)) return;
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/cancel-to-previous`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message);
        showNotification(`Pedido #${orderNumber} cancelado`, 'info');
        setTimeout(() => loadWorkerOrders(), 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Event listeners
function addOrderCardListeners() {
    document.querySelectorAll('.btn-accept').forEach(btn => {
        btn.addEventListener('click', function() {
            acceptOrder(parseInt(this.getAttribute('data-order-id')), this.getAttribute('data-order-number'));
        });
    });
    document.querySelectorAll('.btn-mark-ready').forEach(btn => {
        btn.addEventListener('click', function() {
            markOrderReady(parseInt(this.getAttribute('data-order-id')), this.getAttribute('data-order-number'));
        });
    });
    document.querySelectorAll('.btn-accept-delivery').forEach(btn => {
        btn.addEventListener('click', function() {
            acceptDelivery(parseInt(this.getAttribute('data-order-id')), this.getAttribute('data-order-number'));
        });
    });
    document.querySelectorAll('.btn-mark-paid').forEach(btn => {
        btn.addEventListener('click', function() {
            markOrderPaid(parseInt(this.getAttribute('data-order-id')), this.getAttribute('data-order-number'));
        });
    });
    document.querySelectorAll('.btn-cancel').forEach(btn => {
        btn.addEventListener('click', function() {
            cancelOrder(parseInt(this.getAttribute('data-order-id')), this.getAttribute('data-order-number'));
        });
    });
}

function setupEventListeners() {
    const refreshBtn = document.getElementById('manual-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', () => loadWorkerOrders());
    const logoutBtn = document.getElementById('worker-logout-btn');
    if (logoutBtn) logoutBtn.addEventListener('click', (e) => { e.preventDefault(); workerLogout(); });
}

// Auto-refresh
function startAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => loadWorkerOrders(), REFRESH_INTERVAL_MS);
}

function stopAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = null;
}

// Utilidades
function getTimeAgo(dateString) {
    const seconds = Math.floor((new Date() - new Date(dateString)) / 1000);
    if (seconds < 60) return 'Hace un momento';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)} min`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)} horas`;
    return `Hace ${Math.floor(seconds / 86400)} dias`;
}

function updateLastRefreshTime() {
    const el = document.getElementById('last-refresh-time');
    if (el) el.textContent = `Ultima actualizacion: ${new Date().toLocaleTimeString()}`;
}

// Storage
function loadWorkerFromStorage() {
    const storedData = localStorage.getItem('prontoa_user');
    const userType = localStorage.getItem('prontoa_user_type');
    if (storedData && userType === 'worker') {
        workerData = JSON.parse(storedData);
        updateWorkerInfo();
    }
}

function clearWorkerFromStorage() {
    localStorage.removeItem('prontoa_user');
    localStorage.removeItem('prontoa_user_type');
}

function updateWorkerInfo() {
    const nameEl = document.getElementById('worker-name');
    if (nameEl && workerData) nameEl.textContent = workerData.full_name;
}

// Logout
function workerLogout() {
    if (!confirm('Seguro que deseas cerrar sesion?')) return;
    clearWorkerFromStorage();
    stopAutoRefresh();
    showNotification('Sesion cerrada', 'info');
    setTimeout(() => window.location.href = '/login', 1000);
}

// Notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `<div class="notification-content"><i class="fas fa-${getNotificationIcon(type)}"></i><span>${message}</span></div>`;
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => { if (notification.parentNode) document.body.removeChild(notification); }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = { 'success': 'check-circle', 'error': 'exclamation-circle', 'warning': 'exclamation-triangle', 'info': 'info-circle' };
    return icons[type] || 'info-circle';
}

// Exportar
window.workerApp = { acceptOrder, markOrderReady, acceptDelivery, markOrderPaid, cancelOrder, loadWorkerOrders, workerLogout, startAutoRefresh, stopAutoRefresh };
