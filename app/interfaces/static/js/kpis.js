// KPIs JavaScript - Conectado a API REST real
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos reales de la API
    loadKPIsData();
    
    // Setup event listeners
    setupFilterButtons();
    setupPeriodSelector();
    setupExportButton();
    
    // Animate KPI cards on load
    animateKPICards();
    
    // Actualizar cada 60 segundos
    setInterval(loadKPIsData, 60000);
});

// ============================================================
// CARGAR DATOS DE KPIs DESDE LA API
// ============================================================

async function loadKPIsData(periodDays = 30) {
    try {
        showLoadingState();
        
        // Cargar el resumen completo desde la API
        const response = await fetch(`/api/kpis/summary?period_days=${periodDays}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (!response.ok || !result.success) {
            throw new Error(result.message || 'Error al cargar KPIs');
        }
        
        const summary = result.summary;
        
        // Actualizar la UI con los datos reales
        updateKPICards(summary);
        updateComparisonMetrics({ comparisons: summary.comparisons });
        updateOperationalMetrics({ operational: summary.operational });
        updateFinancialMetrics({ financial: summary.financial });
        updateTrendsChart(summary.hourly_distribution);
        
        hideLoadingState();
        updateLastUpdateTime();
        
    } catch (error) {
        console.error('Error loading KPIs:', error);
        showNotification('Error al cargar métricas', 'error');
        hideLoadingState();
    }
}

// ============================================================
// API CALLS
// ============================================================

async function fetchKPISummary(periodDays = 30) {
    try {
        const response = await fetch(`/api/kpis/summary?period_days=${periodDays}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar resumen de KPIs');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching KPI summary:', error);
        return { success: false, message: error.message };
    }
}

async function fetchKPIComparisons(periodDays = 30) {
    try {
        const response = await fetch(`/api/kpis/comparisons?period_days=${periodDays}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar comparaciones');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching comparisons:', error);
        return { success: false, message: error.message };
    }
}

async function fetchOperationalMetrics(periodDays = 30) {
    try {
        const response = await fetch(`/api/kpis/operational?period_days=${periodDays}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar métricas operacionales');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching operational metrics:', error);
        return { success: false, message: error.message };
    }
}

async function fetchFinancialImpact(periodDays = 30) {
    try {
        const response = await fetch(`/api/kpis/financial?period_days=${periodDays}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar impacto financiero');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching financial impact:', error);
        return { success: false, message: error.message };
    }
}

async function fetchOrdersByHour(days = 7) {
    try {
        const response = await fetch(`/api/kpis/orders-by-hour?days=${days}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al cargar distribución horaria');
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching orders by hour:', error);
        return { success: false, message: error.message };
    }
}

// ============================================================
// UPDATE UI FUNCTIONS
// ============================================================

function updateKPICards(summary) {
    const dashboard = summary.dashboard || {};
    const comparisons = summary.comparisons || {};
    
    // Tiempo de respuesta
    const avgTime = parseFloat(dashboard.avg_response_time) || 0;
    const responseEl = document.getElementById('response-time-value');
    if (responseEl) {
        responseEl.textContent = avgTime.toFixed(1) + 'min';
    }
    
    // Actualizar comparación de tiempo de respuesta
    if (comparisons.avg_response_time || comparisons.response_time) {
        const responseComp = comparisons.avg_response_time || comparisons.response_time;
        const responseChange = document.getElementById('response-time-change');
        const responseTrend = document.getElementById('response-time-trend');
        const responseComparison = document.getElementById('response-time-comparison');
        
        const changePercent = parseFloat(responseComp.change_percent || responseComp.change || 0);
        const previousValue = parseFloat(responseComp.previous || 0);
        
        if (responseChange) {
            responseChange.textContent = (changePercent > 0 ? '+' : '') + changePercent.toFixed(1) + '%';
        }
        
        if (responseTrend) {
            responseTrend.className = 'kpi-trend ' + (changePercent > 0 ? 'positive' : 'negative');
            const icon = responseTrend.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-arrow-' + (changePercent > 0 ? 'up' : 'down');
            }
        }
        
        if (responseComparison) {
            responseComparison.textContent = `vs ${previousValue.toFixed(1)} min anterior`;
        }
    }
    
    // Pedidos procesados
    const ordersCount = parseInt(dashboard.orders_today) || 0;
    const ordersEl = document.getElementById('orders-value');
    if (ordersEl) {
        ordersEl.textContent = ordersCount;
    }
    
    // Actualizar comparación de pedidos
    if (comparisons.total_orders || comparisons.orders_processed) {
        const ordersComp = comparisons.total_orders || comparisons.orders_processed;
        const ordersChange = document.getElementById('orders-change');
        const ordersTrend = document.getElementById('orders-trend');
        const ordersComparison = document.getElementById('orders-comparison');
        
        const changePercent = parseFloat(ordersComp.change_percent || ordersComp.change || 0);
        const previousValue = parseInt(ordersComp.previous || 0);
        
        if (ordersChange) {
            ordersChange.textContent = (changePercent > 0 ? '+' : '') + changePercent.toFixed(1) + '%';
        }
        
        if (ordersTrend) {
            ordersTrend.className = 'kpi-trend ' + (changePercent > 0 ? 'positive' : 'negative');
            const icon = ordersTrend.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-arrow-' + (changePercent > 0 ? 'up' : 'down');
            }
        }
        
        if (ordersComparison) {
            ordersComparison.textContent = `vs ${previousValue} anterior`;
        }
    }
    
    // Tasa de conversión (estimada)
    const satisfaction = parseFloat(dashboard.satisfaction) || 0;
    const conversion = satisfaction > 0 ? (satisfaction * 0.95).toFixed(1) : '0.0';
    const conversionEl = document.getElementById('conversion-value');
    if (conversionEl) {
        conversionEl.textContent = conversion + '%';
    }
    
    // Satisfacción del cliente
    const rating = (satisfaction / 20).toFixed(1); // Convertir de 0-100 a 0-5
    const satisfactionEl = document.getElementById('satisfaction-value');
    if (satisfactionEl) {
        satisfactionEl.textContent = rating + '/5';
    }
    
    // Actualizar comparación de satisfacción
    if (comparisons.customer_satisfaction || comparisons.satisfaction) {
        const satComp = comparisons.customer_satisfaction || comparisons.satisfaction;
        const satisfactionChange = document.getElementById('satisfaction-change');
        const satisfactionTrend = document.getElementById('satisfaction-trend');
        const satisfactionComparison = document.getElementById('satisfaction-comparison');
        
        const changePercent = parseFloat(satComp.change_percent || satComp.change || 0);
        const previousValue = parseFloat(satComp.previous || 0);
        
        if (satisfactionChange) {
            satisfactionChange.textContent = (changePercent > 0 ? '+' : '') + changePercent.toFixed(1) + '%';
        }
        
        if (satisfactionTrend) {
            satisfactionTrend.className = 'kpi-trend ' + (changePercent > 0 ? 'positive' : 'negative');
            const icon = satisfactionTrend.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-arrow-' + (changePercent > 0 ? 'up' : 'down');
            }
        }
        
        if (satisfactionComparison) {
            const previousRating = (previousValue / 20).toFixed(1);
            satisfactionComparison.textContent = `vs ${previousRating} anterior`;
        }
    }
}

function updateComparisonMetrics(data) {
    const comparisons = data.comparisons || {};
    
    // Tiempo de respuesta
    const responseComp = comparisons.avg_response_time || comparisons.response_time;
    if (responseComp) {
        const current = parseFloat(responseComp.current) || 0;
        const previous = parseFloat(responseComp.previous) || 0;
        
        // Actualizar valores
        const afterValueEl = document.getElementById('response-after-value');
        const beforeValueEl = document.getElementById('response-before-value');
        
        if (afterValueEl) afterValueEl.textContent = current.toFixed(1) + ' min';
        if (beforeValueEl) beforeValueEl.textContent = previous.toFixed(1) + ' min';
        
        // Calcular anchos de barras (normalizado al mayor valor)
        const maxValue = Math.max(current, previous, 1); // Evitar división por 0
        const afterBar = document.getElementById('response-after-bar');
        const beforeBar = document.getElementById('response-before-bar');
        
        if (afterBar) afterBar.style.width = ((current / maxValue) * 100) + '%';
        if (beforeBar) beforeBar.style.width = ((previous / maxValue) * 100) + '%';
    }
    
    // Tasa de abandono (estimada desde satisfacción inversa)
    const satComp = comparisons.customer_satisfaction || comparisons.satisfaction;
    if (satComp) {
        const currentSat = parseFloat(satComp.current) || 0;
        const previousSat = parseFloat(satComp.previous) || 0;
        
        // Estimar abandono como inverso de satisfacción (100 - satisfacción)
        const currentAban = 100 - currentSat;
        const previousAban = 100 - previousSat;
        
        const afterValueEl = document.getElementById('abandonment-after-value');
        const beforeValueEl = document.getElementById('abandonment-before-value');
        
        if (afterValueEl) afterValueEl.textContent = currentAban.toFixed(1) + '%';
        if (beforeValueEl) beforeValueEl.textContent = previousAban.toFixed(1) + '%';
        
        const maxValue = Math.max(currentAban, previousAban, 1);
        const afterBar = document.getElementById('abandonment-after-bar');
        const beforeBar = document.getElementById('abandonment-before-bar');
        
        if (afterBar) afterBar.style.width = ((currentAban / maxValue) * 100) + '%';
        if (beforeBar) beforeBar.style.width = ((previousAban / maxValue) * 100) + '%';
    }
    
    // Carga operativa (estimada desde total_orders normalizado)
    const ordersComp = comparisons.total_orders || comparisons.orders_processed;
    if (ordersComp) {
        const current = parseFloat(ordersComp.current) || 0;
        const previous = parseFloat(ordersComp.previous) || 0;
        
        // Normalizar a porcentaje (asumiendo capacidad máxima)
        const maxCapacity = Math.max(current, previous, 1) * 1.2; // 20% más como capacidad
        const currentLoad = (current / maxCapacity) * 100;
        const previousLoad = (previous / maxCapacity) * 100;
        
        const afterValueEl = document.getElementById('workload-after-value');
        const beforeValueEl = document.getElementById('workload-before-value');
        
        if (afterValueEl) afterValueEl.textContent = currentLoad.toFixed(0) + '%';
        if (beforeValueEl) beforeValueEl.textContent = previousLoad.toFixed(0) + '%';
        
        const afterBar = document.getElementById('workload-after-bar');
        const beforeBar = document.getElementById('workload-before-bar');
        
        if (afterBar) afterBar.style.width = currentLoad + '%';
        if (beforeBar) beforeBar.style.width = previousLoad + '%';
    }
}

function updateOperationalMetrics(data) {
    const operational = data.operational || {};
    
    // Tasa de automatización
    const automationEl = document.getElementById('automation-rate-value');
    if (automationEl && operational.automation_rate !== undefined) {
        const rate = parseFloat(operational.automation_rate) || 0;
        automationEl.textContent = rate.toFixed(1) + '%';
    }
    
    // Tiempo ahorrado (usar time_saved_weekly_hours que es lo que devuelve la API)
    const timeSavedEl = document.getElementById('time-saved-value');
    if (timeSavedEl) {
        const hours = parseFloat(operational.time_saved_weekly_hours || operational.time_saved_per_week || 0);
        timeSavedEl.textContent = hours.toFixed(1) + 'h';
    }
    
    // Precisión de IA
    const aiAccuracyEl = document.getElementById('ai-accuracy-value');
    if (aiAccuracyEl && operational.ai_accuracy !== undefined) {
        const accuracy = parseFloat(operational.ai_accuracy) || 0;
        aiAccuracyEl.textContent = accuracy.toFixed(1) + '%';
    }
    
    // Tasa de error
    const errorRateEl = document.getElementById('error-rate-value');
    if (errorRateEl && operational.error_rate !== undefined) {
        const errorRate = parseFloat(operational.error_rate) || 0;
        errorRateEl.textContent = errorRate.toFixed(2) + '%';
    }
}

function updateFinancialMetrics(data) {
    const financial = data.financial || {};
    
    // Incremento en ventas (revenue impact)
    const revenueEl = document.getElementById('revenue-impact-value');
    const revenueTrendEl = document.getElementById('revenue-impact-trend');
    
    if (revenueEl) {
        // Usar sales_increase que es lo que devuelve la API
        const revenue = parseFloat(financial.sales_increase || financial.revenue_impact || 0);
        revenueEl.textContent = formatCurrency(revenue);
    }
    
    if (revenueTrendEl) {
        // Usar sales_increase_percentage que es lo que devuelve la API
        const percent = parseFloat(financial.sales_increase_percentage || financial.sales_increase_percent || 0);
        revenueTrendEl.textContent = (percent > 0 ? '+' : '') + percent.toFixed(1) + '% vs mes anterior';
    }
    
    // Ahorro operativo (cost reduction)
    const savingsEl = document.getElementById('cost-reduction-value');
    const savingsTrendEl = document.getElementById('cost-reduction-trend');
    
    if (savingsEl) {
        // Usar operational_savings que es lo que devuelve la API
        const savings = parseFloat(financial.operational_savings || financial.cost_reduction || 0);
        savingsEl.textContent = formatCurrency(savings);
    }
    
    if (savingsTrendEl) {
        savingsTrendEl.textContent = 'Reducción de costos';
    }
    
    // ROI
    const roiEl = document.getElementById('roi-value');
    const roiTrendEl = document.getElementById('roi-trend');
    
    if (roiEl) {
        // Usar roi que es lo que devuelve la API (ya viene en porcentaje)
        const roi = parseFloat(financial.roi || financial.roi_percent || 0);
        roiEl.textContent = roi.toFixed(0) + '%';
    }
    
    if (roiTrendEl) {
        const roi = parseFloat(financial.roi || financial.roi_percent || 0);
        if (roi > 300) {
            roiTrendEl.textContent = 'Excelente rendimiento';
        } else if (roi > 150) {
            roiTrendEl.textContent = 'Buen rendimiento';
        } else if (roi > 0) {
            roiTrendEl.textContent = 'Rendimiento positivo';
        } else {
            roiTrendEl.textContent = 'En desarrollo';
        }
    }
}

function updateTrendsChart(ordersByHourData, retryCount = 0) {
    const MAX_RETRIES = 5;
    
    // Verificar si Chart.js está cargado
    if (typeof Chart === 'undefined') {
        if (retryCount < MAX_RETRIES) {
            setTimeout(() => updateTrendsChart(ordersByHourData, retryCount + 1), 500);
        }
        return;
    }
    
    // Inicializar el gráfico si no existe
    if (!window.trendsChart) {
        const initResult = initializeTrendsChart();
        
        // Dar tiempo para que se inicialice si falló
        if (!initResult || !window.trendsChart || typeof window.trendsChart.data === 'undefined') {
            if (retryCount < MAX_RETRIES) {
                setTimeout(() => updateTrendsChart(ordersByHourData, retryCount + 1), 500);
                return;
            }
            return;
        }
    }
    
    const chart = window.trendsChart;
    
    // Si window.trendsChart es un canvas en lugar de un Chart, reintentar
    if (chart && chart.tagName === 'CANVAS') {
        window.trendsChart = null;
        if (retryCount < MAX_RETRIES) {
            setTimeout(() => updateTrendsChart(ordersByHourData, retryCount + 1), 500);
        }
        return;
    }
    
    if (!chart || !chart.data) {
        return;
    }
    
    if (!ordersByHourData || typeof ordersByHourData !== 'object') {
        // Mostrar gráfico vacío
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update('active');
        return;
    }
    
    // Preparar datos para el gráfico
    const hours = Object.keys(ordersByHourData).sort((a, b) => parseInt(a) - parseInt(b));
    const orderCounts = hours.map(hour => ordersByHourData[hour] || 0);
    
    // Actualizar datos del gráfico
    chart.data.labels = hours.map(h => `${h}:00`);
    chart.data.datasets[0].data = orderCounts;
    chart.update('active');
}

// Initialize the main trends chart
function initializeTrendsChart() {
    const canvas = document.getElementById('trendsChart');
    if (!canvas) {
        return false;
    }
    
    if (typeof Chart === 'undefined') {
        return false;
    }
    
    try {
        // Chart.js puede aceptar tanto el canvas como el contexto 2D
        // Pasamos directamente el canvas y Chart.js lo maneja internamente
        const chart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Pedidos por Hora',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#374151',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: {
                        color: '#f3f4f6'
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            size: 11
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6,
                    backgroundColor: 'white',
                    borderWidth: 2
                }
            }
        }
    });
    
    // Store chart instance for filtering
    window.trendsChart = chart;
    return true;
    
    } catch (error) {
        console.error('Error al inicializar gráfico de tendencias:', error);
        return false;
    }
}

// Setup filter buttons functionality
function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Reload data based on filter
            const filterType = this.textContent.toLowerCase();
            handleFilterChange(filterType);
        });
    });
}

function handleFilterChange(filterType) {
    // Recargar datos según el filtro seleccionado
    loadKPIsData();
}

// Setup period selector functionality
function setupPeriodSelector() {
    const periodSelector = document.querySelector('.period-selector');
    
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            updateDataByPeriod(this.value);
        });
    }
}

// Update data based on selected period
function updateDataByPeriod(period) {
    const periodDaysMap = {
        'today': 1,
        'week': 7,
        'month': 30,
        'quarter': 90
    };
    
    const days = periodDaysMap[period] || 30;
    loadKPIsData(days);
}

// Setup export functionality
function setupExportButton() {
    const exportButton = document.querySelector('.btn-export');
    
    if (exportButton) {
        exportButton.addEventListener('click', async function() {
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exportando...';
            this.disabled = true;
            
            try {
                // Obtener datos actuales
                const result = await fetchKPISummary(30);
                
                if (result.success) {
                    downloadCSV(result.data);
                    showNotification('Reporte exportado exitosamente', 'success');
                } else {
                    showNotification('Error al exportar reporte', 'error');
                }
            } catch (error) {
                console.error('Error exporting:', error);
                showNotification('Error al exportar reporte', 'error');
            } finally {
                // Reset button state
                this.innerHTML = originalText;
                this.disabled = false;
            }
        });
    }
}

// Generate and download CSV report
function downloadCSV(data) {
    const dashboard = data.dashboard || {};
    const operational = data.operational || {};
    const financial = data.financial || {};
    
    const csvContent = `Métrica,Valor
Pedidos Hoy,${dashboard.orders_today || 0}
Tiempo de Respuesta (min),${(dashboard.avg_response_time || 0).toFixed(1)}
Ventas Hoy,${formatCurrency(dashboard.sales_today || 0)}
Satisfacción (%),${(dashboard.satisfaction || 0).toFixed(1)}
Tasa de Automatización (%),${(operational.automation_rate || 0).toFixed(1)}
Tiempo Ahorrado (h/semana),${(operational.time_saved_per_week || 0).toFixed(1)}
Precisión IA (%),${(operational.ai_accuracy || 0).toFixed(1)}
Tasa de Error (%),${(operational.error_rate || 0).toFixed(2)}
Incremento en Ventas (%),${(financial.sales_increase_percent || 0).toFixed(1)}
ROI (%),${(financial.roi_percent || 0).toFixed(0)}
Ahorro Operativo,${formatCurrency(financial.operational_savings || 0)}`;

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `kpis-report-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Animate KPI cards on page load
function animateKPICards() {
    const kpiCards = document.querySelectorAll('.kpi-card');
    
    kpiCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
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

function updateLastUpdateTime() {
    const lastUpdate = document.querySelector('.last-update');
    if (lastUpdate) {
        const now = new Date();
        lastUpdate.textContent = `Última actualización: ${now.toLocaleTimeString('es-CO')}`;
    }
}

function showLoadingState() {
    const container = document.querySelector('.kpis-container');
    if (container) {
        container.style.opacity = '0.6';
        container.style.pointerEvents = 'none';
    }
}

function hideLoadingState() {
    const container = document.querySelector('.kpis-container');
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