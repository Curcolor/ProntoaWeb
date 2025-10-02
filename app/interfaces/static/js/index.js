// JavaScript específico para la página de inicio de Prontoa
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página de inicio de Prontoa cargada');
    
    // Inicializar funcionalidades específicas de la landing page
    initializeLandingPage();
});

/**
 * Inicializa todas las funcionalidades de la landing page
 */
function initializeLandingPage() {
    setupSmoothScrolling();
    setupScrollAnimations();
    setupNavbarScrollEffect();
    setupCTAButtons();
    setupPricingCards();
}

/**
 * Configura el smooth scrolling para enlaces de anclaje
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                // Obtener altura del navbar fijo
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.offsetTop - navbarHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Configura las animaciones al hacer scroll
 */
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Retraso escalonado para animaciones más fluidas
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.classList.add('animate-in');
                }, index * 100);
            }
        });
    }, observerOptions);

    // Aplicar animaciones a elementos específicos
    const animatedElements = document.querySelectorAll(`
        .problem-card, 
        .feature-item, 
        .benefit-card, 
        .pricing-card,
        .hero-stats .stat-item
    `);
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

/**
 * Efectos del navbar al hacer scroll
 */
function setupNavbarScrollEffect() {
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        const currentScrollY = window.scrollY;
        
        // Cambiar estilo del navbar basado en la posición del scroll
        if (currentScrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            navbar.style.background = 'white';
            navbar.style.backdropFilter = 'none';
            navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        }
        
        // Ocultar/mostrar navbar al hacer scroll hacia abajo/arriba
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
}

/**
 * Configurar botones de Call-to-Action
 */
function setupCTAButtons() {
    // Botones del hero
    const demoButton = document.querySelector('.btn-primary-hero');
    const videoButton = document.querySelector('.btn-secondary-hero');
    
    if (demoButton) {
        demoButton.addEventListener('click', function() {
            // Aquí iría la lógica para solicitar demo
            showDemoModal();
        });
    }
    
    if (videoButton) {
        videoButton.addEventListener('click', function() {
            // Aquí iría la lógica para mostrar video demo
            scrollToSection('#demo');
        });
    }
    
    // Botones de pricing
    document.querySelectorAll('.pricing-card .btn-trial').forEach(button => {
        button.addEventListener('click', function() {
            const planName = this.closest('.pricing-card').querySelector('.pricing-title').textContent;
            handlePricingSelection(planName, this.textContent);
        });
    });
    
    // Botones del navbar
    document.querySelectorAll('.btn-login, .btn-trial').forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('btn-login')) {
                // Redirigir a página de login
                window.location.href = '/login';
            } else {
                // Mostrar modal de registro
                showTrialModal();
            }
        });
    });
}

/**
 * Configurar efectos de las tarjetas de pricing
 */
function setupPricingCards() {
    document.querySelectorAll('.pricing-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Efecto de hover mejorado
            this.style.transform = 'translateY(-15px) scale(1.02)';
            this.style.boxShadow = '0 25px 50px rgba(37, 211, 102, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('featured')) {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.08)';
            } else {
                this.style.transform = 'scale(1.05)';
                this.style.boxShadow = '0 20px 60px rgba(0,0,0,0.15)';
            }
        });
    });
}

/**
 * Muestra modal para solicitar demo
 */
function showDemoModal() {
    // Crear modal dinámicamente
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Solicitar Demo Personalizada</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="demoForm">
                        <div class="mb-3">
                            <label for="businessName" class="form-label">Nombre del Negocio</label>
                            <input type="text" class="form-control" id="businessName" required>
                        </div>
                        <div class="mb-3">
                            <label for="contactEmail" class="form-label">Email de Contacto</label>
                            <input type="email" class="form-control" id="contactEmail" required>
                        </div>
                        <div class="mb-3">
                            <label for="phoneNumber" class="form-label">Número de WhatsApp</label>
                            <input type="tel" class="form-control" id="phoneNumber" required>
                        </div>
                        <div class="mb-3">
                            <label for="orderVolume" class="form-label">Pedidos promedio por día</label>
                            <select class="form-control" id="orderVolume" required>
                                <option value="">Seleccionar...</option>
                                <option value="1-20">1-20 pedidos</option>
                                <option value="21-50">21-50 pedidos</option>
                                <option value="51-100">51-100 pedidos</option>
                                <option value="100+">Más de 100 pedidos</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="submitDemoRequest()">Solicitar Demo</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Limpiar modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

/**
 * Muestra modal para prueba gratis
 */
function showTrialModal() {
    window.ProntoaWeb.showToast('Funcionalidad de registro en desarrollo', 'info');
}

/**
 * Maneja la selección de plan de pricing
 */
function handlePricingSelection(planName, buttonText) {
    if (buttonText === 'Contactar Ventas') {
        // Abrir modal de contacto
        window.location.href = 'mailto:ventas@prontoa.com?subject=Consulta Plan Enterprise';
    } else {
        // Mostrar modal de registro
        window.ProntoaWeb.showToast(`Seleccionaste el plan ${planName}`, 'success');
        showTrialModal();
    }
}

/**
 * Envía solicitud de demo
 */
function submitDemoRequest() {
    const form = document.getElementById('demoForm');
    const formData = new FormData(form);
    
    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Simular envío (aquí iría la llamada real a la API)
    window.ProntoaWeb.showToast('Solicitud de demo enviada exitosamente. Te contactaremos pronto.', 'success');
    
    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
    modal.hide();
    
    // Enviar datos a Google Analytics (opcional)
    if (typeof gtag !== 'undefined') {
        gtag('event', 'demo_request', {
            'event_category': 'engagement',
            'event_label': 'landing_page'
        });
    }
}

/**
 * Scroll suave a una sección específica
 */
function scrollToSection(selector) {
    const element = document.querySelector(selector);
    if (element) {
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        const targetPosition = element.offsetTop - navbarHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Tracking de eventos (opcional para analytics)
 */
function trackEvent(eventName, parameters = {}) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, parameters);
    }
    
    // Facebook Pixel
    if (typeof fbq !== 'undefined') {
        fbq('track', eventName, parameters);
    }
    
    console.log('Event tracked:', eventName, parameters);
}

// Exportar funciones para uso global
window.ProntoaLanding = {
    scrollToSection,
    showDemoModal,
    trackEvent
};
