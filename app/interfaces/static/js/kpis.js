// KPIs JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initializeTrendsChart();
    
    // Setup event listeners
    setupFilterButtons();
    setupPeriodSelector();
    setupExportButton();
    
    // Animate KPI cards on load
    animateKPICards();
});

// Initialize the main trends chart
function initializeTrendsChart() {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) return;
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct'],
            datasets: [
                {
                    label: 'Tiempo de Respuesta (min)',
                    data: [18, 16, 14, 12, 8, 6, 4.5, 3.8, 3.5, 3.2],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Satisfacción del Cliente',
                    data: [4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.8, 4.8, 4.8],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                },
                {
                    label: 'Tasa de Conversión (%)',
                    data: [74, 76, 78, 82, 85, 88, 90, 92, 94, 94.8],
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
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
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
            
            // Update chart based on filter
            updateChartData(this.textContent.toLowerCase());
        });
    });
}

// Update chart data based on selected filter
function updateChartData(filter) {
    if (!window.trendsChart) return;
    
    const chart = window.trendsChart;
    
    // Define different datasets for each filter
    const datasets = {
        tiempos: [
            {
                label: 'Tiempo de Respuesta (min)',
                data: [18, 16, 14, 12, 8, 6, 4.5, 3.8, 3.5, 3.2],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }
        ],
        pedidos: [
            {
                label: 'Pedidos Procesados',
                data: [145, 167, 189, 203, 234, 256, 278, 289, 298, 287],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }
        ],
        conversión: [
            {
                label: 'Tasa de Conversión (%)',
                data: [74, 76, 78, 82, 85, 88, 90, 92, 94, 94.8],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }
        ]
    };
    
    // Update chart with new data
    chart.data.datasets = datasets[filter] || datasets.tiempos;
    chart.update('active');
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
    // Simulate data updates based on period
    const kpiValues = document.querySelectorAll('.kpi-value');
    
    // Define different values for each period
    const periodData = {
        today: ['2.8min', '12', '96.2%', '4.9/5'],
        week: ['3.0min', '87', '95.1%', '4.8/5'],
        month: ['3.2min', '287', '94.8%', '4.8/5'],
        quarter: ['3.5min', '856', '93.2%', '4.7/5']
    };
    
    const values = periodData[period] || periodData.month;
    
    // Animate value changes
    kpiValues.forEach((element, index) => {
        if (values[index]) {
            element.style.transform = 'scale(0.8)';
            element.style.opacity = '0.5';
            
            setTimeout(() => {
                element.textContent = values[index];
                element.style.transform = 'scale(1)';
                element.style.opacity = '1';
            }, 150);
        }
    });
}

// Setup export functionality
function setupExportButton() {
    const exportButton = document.querySelector('.btn-export');
    
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exportando...';
            this.disabled = true;
            
            // Simulate export process
            setTimeout(() => {
                // Create and download a mock CSV file
                downloadCSV();
                
                // Reset button state
                this.innerHTML = originalText;
                this.disabled = false;
                
                // Show success message
                showNotification('Reporte exportado exitosamente', 'success');
            }, 2000);
        });
    }
}

// Generate and download CSV report
function downloadCSV() {
    const csvContent = `Métrica,Valor Actual,Valor Anterior,Mejora
Tiempo de Respuesta,3.2 min,18 min,+72%
Pedidos Procesados,287,198,+45%
Tasa de Conversión,94.8%,74%,+28%
Satisfacción del Cliente,4.8/5,4.2/5,+15%
Automatización,98.5%,30%,+68%
Ahorro Semanal,42h,12h,+350%
ROI,485%,150%,+223%`;

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

// Show notification messages
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Update real-time metrics (simulate live updates)
function startRealTimeUpdates() {
    setInterval(() => {
        // Simulate small random changes in metrics
        const kpiValues = document.querySelectorAll('.kpi-value');
        
        kpiValues.forEach(element => {
            const currentValue = element.textContent;
            
            // Add subtle animation to indicate real-time updates
            if (Math.random() > 0.8) { // 20% chance of update
                element.style.background = 'rgba(16, 185, 129, 0.1)';
                element.style.borderRadius = '4px';
                element.style.padding = '2px 4px';
                
                setTimeout(() => {
                    element.style.background = 'transparent';
                    element.style.padding = '0';
                }, 1000);
            }
        });
    }, 30000); // Update every 30 seconds
}

// Initialize real-time updates
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(startRealTimeUpdates, 5000); // Start after 5 seconds
});