// Dashboard JavaScript - Conectado a API REST real

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded - Using real API');
    
    // Cargar datos iniciales
    loadDashboardData();
    
    // Inicializar tooltips
    initializeTooltips();
    
    // Configurar drag and drop para Kanban
    initializeKanbanDragDrop();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Actualizar cada 30 segundos
    setInterval(loadDashboardData, 30000);
});

// Prueba de obtener nombre de usuario --------------------------------------------------------------------------------------------------------------------------------------
document.getElementById('obtener-info-btn').addEventListener('click', async function() {
    const respuesta = await fetch('/api/auth/me');
    const data = await respuesta.json();


    document.getElementById('resultado').textContent = data.success;
    document.getElementById('user-name').textContent = data.user.full_name;
    document.getElementById('user-email').textContent = data.user.email;
    document.getElementById('user-phone').textContent = data.user.phone;
});

document.getElementById('actualizar-nombre-btn').addEventListener('click', async function() {
    const nuevoNombre = document.getElementById('nuevo-nombre').value;
    const token = getCsrfToken();

    const respuesta = await fetch('/api/auth/update_name', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': token
         },
        body: JSON.stringify({ new_name: nuevoNombre })
    });

    const data = await respuesta.json();
    document.getElementById('user-name').textContent = data.user.full_name;
});

document.getElementById('obtener-trabajador-btn').addEventListener('click', async function() {

    const idtrabajador = document.getElementById('trabajador-id').value;

    const respuesta = await fetch(`/api/workers/${idtrabajador}`);

    const data = await respuesta.json();

    document.getElementById('trabajador-nombre').textContent = data.worker.full_name;
    document.getElementById('trabajador-email').textContent = data.worker.email;
    document.getElementById('trabajador-telefono').textContent = data.worker.phone;
    
});

// ============================================================
// CARGAR DATOS DEL DASHBOARD
// ============================================================

async function loadDashboardData() {
    try {
        console.log('🚀 Loading dashboard data...');
        showLoadingState();
        
        // Cargar pedidos y métricas en paralelo
        const [ordersResult, metricsResult] = await Promise.all([
            fetchOrders(),
            fetchDashboardMetrics()
        ]);
        
        console.log('📊 Results received:', { ordersResult, metricsResult });
        
        if (ordersResult.success) {
            console.log('✅ Rendering kanban with orders:', ordersResult.orders?.length);
            renderKanbanBoard(ordersResult.orders);
            updateColumnCounts(ordersResult.by_status);
        } else {
            console.error('❌ Failed to load orders:', ordersResult.message);
        }
        
        if (metricsResult.success) {
            console.log('✅ Updating metrics:', metricsResult.metrics);
            updateDashboardMetrics(metricsResult.metrics);
        } else {
            console.error('❌ Failed to load metrics:', metricsResult.message);
        }
        
        hideLoadingState();
        updateLastUpdateTime();
        
    } catch (error) {
        console.error('❌ Error loading dashboard:', error);
        showNotification('Error al cargar el dashboard', 'error');
        hideLoadingState();
    }
}

// ============================================================
// API CALLS - Fetch Functions
// ============================================================

async function fetchOrders(status = null) {
    try {
        console.log('🔄 Fetching orders...', status ? `status=${status}` : 'all');
        const url = status ? `/api/orders?status=${status}` : '/api/orders';
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📦 Orders response status:', response.status);
        
        // Si no está autenticado, redirigir al login
        if (response.status === 401) {
            console.error('❌ Not authenticated, redirecting to login...');
            window.location.href = '/login';
            return { success: false, message: 'No autenticado' };
        }
        
        const data = await response.json();
        console.log('📦 Orders data:', data);
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar pedidos');
        }
        
        return data;
    } catch (error) {
        console.error('❌ Error fetching orders:', error);
        return { success: false, message: error.message };
    }
}

async function fetchDashboardMetrics() {
    try {
        console.log('🔄 Fetching dashboard metrics...');
        const response = await fetch('/api/kpis/dashboard', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📊 Metrics response status:', response.status);
        
        // Si no está autenticado, redirigir al login
        if (response.status === 401) {
            console.error('❌ Not authenticated, redirecting to login...');
            window.location.href = '/login';
            return { success: false, message: 'No autenticado' };
        }
        
        const data = await response.json();
        console.log('📊 Metrics data:', data);
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar métricas');
        }
        
        return data;
    } catch (error) {
        console.error('❌ Error fetching metrics:', error);
        return { success: false, message: error.message };
    }
}

async function updateOrderStatus(orderId, newStatus) {
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al actualizar pedido');
        }
        
        return data;
    } catch (error) {
        console.error('Error updating order status:', error);
        return { success: false, message: error.message };
    }
}

async function cancelOrder(orderId, reason) {
    try {
        const token = getCsrfToken();
        const response = await fetch(`/api/orders/${orderId}/cancel`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token
            },
            body: JSON.stringify({ reason: reason })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cancelar pedido');
        }
        
        return data;
    } catch (error) {
        console.error('Error canceling order:', error);
        return { success: false, message: error.message };
    }
}

// ============================================================
// RENDER FUNCTIONS
// ============================================================

function renderKanbanBoard(orders) {
    // Agrupar pedidos por estado
    const ordersByStatus = {
        received: [],
        preparing: [],
        ready: [],
        sent: [],
        paid: [],
        closed: []
    };
    
    orders.forEach(order => {
        if (ordersByStatus[order.status] !== undefined) {
            ordersByStatus[order.status].push(order);
        }
    });
    
    // Renderizar cada columna
    Object.keys(ordersByStatus).forEach(status => {
        const column = document.querySelector(`[data-status="${status}"] .kanban-cards`);
        if (column) {
            column.innerHTML = '';
            ordersByStatus[status].forEach(order => {
                column.appendChild(createOrderCard(order));
            });
        }
    });
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.draggable = true;
    card.dataset.orderId = order.id;
    card.dataset.orderStatus = order.status;
    
    // Calcular tiempo transcurrido
    const createdDate = new Date(order.created_at);
    const timeAgo = getTimeAgo(createdDate);
    
    // Formatear total
    const total = formatCurrency(order.total_amount);
    
    // Obtener información del cliente
    const customerName = order.customer?.name || 'Cliente';
    const customerPhone = order.customer?.phone || '';
    
    // Tipo de pedido
    const orderTypeIcon = order.order_type === 'delivery' ? 'fa-motorcycle' : 'fa-shopping-bag';
    const orderTypeLabel = order.order_type === 'delivery' ? 'Delivery' : 'Pickup';
    
    card.innerHTML = `
        <div class="order-header">
            <span class="order-number">#${order.order_number}</span>
            <span class="order-time">${timeAgo}</span>
        </div>
        <div class="order-customer">
            <i class="fas fa-user"></i>
            <strong>${customerName}</strong>
        </div>
        ${customerPhone ? `<div class="order-phone"><i class="fas fa-phone"></i> ${customerPhone}</div>` : ''}
        <div class="order-type">
            <i class="fas ${orderTypeIcon}"></i>
            <span>${orderTypeLabel}</span>
        </div>
        <div class="order-items">
            <i class="fas fa-shopping-cart"></i>
            <span>${order.items?.length || 0} producto(s)</span>
        </div>
        ${order.notes ? `<div class="order-notes"><i class="fas fa-sticky-note"></i> ${order.notes}</div>` : ''}
        <div class="order-footer">
            <span class="order-total">${total}</span>
            <button class="btn-view-details" onclick="showOrderDetails(${order.id})">
                <i class="fas fa-eye"></i>
            </button>
        </div>
    `;
    
    // Event listeners para drag & drop
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
    
    return card;
}

function updateColumnCounts(byStatus) {
    const statusMap = {
        received: 'Recibidos',
        preparing: 'En preparación',
        ready: 'Listos',
        sent: 'En camino',
        paid: 'Pagados',
        closed: 'Cerrados'
    };

    Object.keys(statusMap).forEach(status => {
        const column = document.querySelector(`[data-status="${status}"]`);
        if (!column) {
            return;
        }

        const headerContainer = column.querySelector('.kanban-column-header') || column.querySelector('.column-header');
        const headerTitle = headerContainer ? headerContainer.querySelector('h3') : null;
        const countBadge = headerContainer ? headerContainer.querySelector('.kanban-count') : column.querySelector('.kanban-count');
        const count = byStatus[status] || 0;

        if (headerTitle) {
            headerTitle.textContent = statusMap[status];
        }

        if (countBadge) {
            countBadge.textContent = count;
        } else if (headerTitle) {
            headerTitle.textContent = `${statusMap[status]} (${count})`;
        }
    });
}

function updateDashboardMetrics(metrics) {
    // Actualizar pedidos de hoy
    const ordersToday = document.getElementById('orders-today');
    if (ordersToday) {
        ordersToday.textContent = parseInt(metrics.orders_today) || 0;
    }
    
    // Actualizar tiempo promedio de respuesta
    const avgResponse = document.getElementById('avg-response-time');
    if (avgResponse) {
        const avgTime = parseFloat(metrics.avg_response_time) || 0;
        avgResponse.textContent = avgTime.toFixed(1) + ' min';
    }
    
    // Actualizar ventas de hoy
    const salesToday = document.getElementById('sales-today');
    if (salesToday) {
        salesToday.textContent = formatCurrency(metrics.sales_today || 0);
    }
    
    // Actualizar satisfacción
    const satisfaction = document.getElementById('satisfaction');
    if (satisfaction) {
        const satisfactionValue = parseFloat(metrics.satisfaction) || 0;
        satisfaction.textContent = satisfactionValue.toFixed(1) + '%';
    }
}

// ============================================================
// KANBAN DRAG & DROP
// ============================================================

let draggedCard = null;

function initializeKanbanDragDrop() {
    const columns = document.querySelectorAll('.kanban-column');
    
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
    });
}

function handleDragStart(e) {
    draggedCard = e.currentTarget;
    e.currentTarget.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.currentTarget.innerHTML);
}

function handleDragEnd(e) {
    e.currentTarget.style.opacity = '1';
    
    // Remover clases de drag-over
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    
    e.dataTransfer.dropEffect = 'move';
    e.currentTarget.classList.add('drag-over');
    
    return false;
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

async function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    if (!draggedCard) return;
    
    const column = e.currentTarget.closest('.kanban-column');
    const newStatus = column.dataset.status;
    const orderId = draggedCard.dataset.orderId;
    const currentStatus = draggedCard.dataset.orderStatus;
    
    // No hacer nada si el estado no cambió
    if (newStatus === currentStatus) return;
    
    // Validar transición de estado
    if (!isValidStatusTransition(currentStatus, newStatus)) {
        showNotification('Transición de estado no válida', 'error');
        return;
    }
    
    // Actualizar el pedido en el servidor
    const result = await updateOrderStatus(orderId, newStatus);
    
    if (result.success) {
        showNotification(`Pedido #${result.order.order_number} actualizado a ${getStatusLabel(newStatus)}`, 'success');
        
        // Recargar el dashboard
        loadDashboardData();
    } else {
        showNotification(result.message || 'Error al actualizar el pedido', 'error');
    }
    
    draggedCard = null;
}

function isValidStatusTransition(currentStatus, newStatus) {
    const validTransitions = {
        received: ['preparing', 'cancelled'],
        preparing: ['ready', 'cancelled'],
        ready: ['sent', 'cancelled'],
        sent: ['paid', 'cancelled']
    };
    
    return validTransitions[currentStatus]?.includes(newStatus) || false;
}

function getStatusLabel(status) {
    const labels = {
        received: 'Recibido',
        preparing: 'En Preparación',
        ready: 'Listo',
        sent: 'Enviado',
        paid: 'Pagado',
        closed: 'Cerrado',
        cancelled: 'Cancelado'
    };
    
    return labels[status] || status;
}

// ============================================================
// MODAL DE DETALLES DEL PEDIDO
// ============================================================

async function showOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.message || 'Error al cargar detalles del pedido');
        }
        
        renderOrderDetailsModal(data.order);
        
    } catch (error) {
        console.error('Error loading order details:', error);
        showNotification('Error al cargar detalles del pedido', 'error');
    }
}

function renderOrderDetailsModal(order) {
    // Crear modal si no existe
    let modal = document.getElementById('orderDetailsModal');
    if (!modal) {
        modal = createOrderDetailsModal();
        document.body.appendChild(modal);
    }
    
    // Rellenar contenido
    const modalBody = modal.querySelector('.modal-body');
    
    modalBody.innerHTML = `
        <div class="order-details-content">
            <div class="detail-section">
                <h4>Información del Pedido</h4>
                <p><strong>Número:</strong> #${order.order_number}</p>
                <p><strong>Estado:</strong> <span class="badge badge-${order.status}">${getStatusLabel(order.status)}</span></p>
                <p><strong>Tipo:</strong> ${order.order_type === 'delivery' ? 'Delivery' : 'Pickup'}</p>
                <p><strong>Fecha:</strong> ${formatDate(order.created_at)}</p>
            </div>
            
            <div class="detail-section">
                <h4>Cliente</h4>
                <p><strong>Nombre:</strong> ${order.customer?.name || 'N/A'}</p>
                <p><strong>Teléfono:</strong> ${order.customer?.phone || 'N/A'}</p>
                ${order.delivery_address ? `<p><strong>Dirección:</strong> ${order.delivery_address}</p>` : ''}
            </div>
            
            <div class="detail-section">
                <h4>Productos</h4>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${order.items?.map(item => `
                            <tr>
                                <td>${item.product_name || 'Producto'}</td>
                                <td>${item.quantity}</td>
                                <td>${formatCurrency(item.unit_price)}</td>
                                <td>${formatCurrency(item.subtotal)}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="4">No hay productos</td></tr>'}
                    </tbody>
                    <tfoot>
                        <tr>
                            <th colspan="3">Total</th>
                            <th>${formatCurrency(order.total_amount)}</th>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            ${order.notes ? `
                <div class="detail-section">
                    <h4>Notas</h4>
                    <p>${order.notes}</p>
                </div>
            ` : ''}
            
            <div class="detail-section">
                <h4>Métricas</h4>
                ${order.response_time_seconds ? `<p><strong>Tiempo de respuesta:</strong> ${Math.floor(order.response_time_seconds / 60)} min</p>` : ''}
                ${order.preparation_time_seconds ? `<p><strong>Tiempo de preparación:</strong> ${Math.floor(order.preparation_time_seconds / 60)} min</p>` : ''}
            </div>
            
            <div class="detail-actions">
                <button class="btn btn-danger" onclick="handleCancelOrder(${order.id})">
                    <i class="fas fa-times"></i> Cancelar Pedido
                </button>
                <button class="btn btn-secondary" onclick="closeOrderDetailsModal()">
                    Cerrar
                </button>
            </div>
        </div>
    `;
    
    // Mostrar modal
    modal.style.display = 'block';
    modal.classList.add('show');
}

function createOrderDetailsModal() {
    const modal = document.createElement('div');
    modal.id = 'orderDetailsModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Detalles del Pedido</h3>
                    <button class="close-btn" onclick="closeOrderDetailsModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body"></div>
            </div>
        </div>
    `;
    
    // Click fuera del modal para cerrar
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeOrderDetailsModal();
        }
    });
    
    return modal;
}

function closeOrderDetailsModal() {
    const modal = document.getElementById('orderDetailsModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
}

async function handleCancelOrder(orderId) {
    const reason = prompt('¿Por qué deseas cancelar este pedido?');
    
    if (!reason) {
        return; // Usuario canceló
    }
    
    const result = await cancelOrder(orderId, reason);
    
    if (result.success) {
        showNotification('Pedido cancelado correctamente', 'success');
        closeOrderDetailsModal();
        loadDashboardData();
    } else {
        showNotification(result.message || 'Error al cancelar el pedido', 'error');
    }
}

// ============================================================
// EVENT LISTENERS
// ============================================================

function setupEventListeners() {
    // Botón de refrescar
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadDashboardData();
            showNotification('Dashboard actualizado', 'info');
        });
    }
    
    // Filtros de estado
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const status = this.dataset.status;
            filterByStatus(status);
        });
    });
}

async function filterByStatus(status) {
    const result = await fetchOrders(status);
    
    if (result.success) {
        renderKanbanBoard(result.orders);
        showNotification(`Mostrando pedidos: ${getStatusLabel(status)}`, 'info');
    }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount || 0);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (days > 0) return `Hace ${days}d`;
    if (hours > 0) return `Hace ${hours}h`;
    if (minutes > 0) return `Hace ${minutes}m`;
    return 'Ahora';
}

function updateLastUpdateTime() {
    const lastUpdate = document.querySelector('.last-update');
    if (lastUpdate) {
        const now = new Date();
        lastUpdate.textContent = `Última actualización: ${now.toLocaleTimeString('es-CO')}`;
    }
}

function showLoadingState() {
    const container = document.querySelector('.kanban-board');
    if (container) {
        container.style.opacity = '0.6';
        container.style.pointerEvents = 'none';
    }
}

function hideLoadingState() {
    const container = document.querySelector('.kanban-board');
    if (container) {
        container.style.opacity = '1';
        container.style.pointerEvents = 'auto';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}
