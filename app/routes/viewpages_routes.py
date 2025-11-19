"""
Blueprint para las páginas web de la interfaz de usuario.
Maneja las rutas que renderizan templates HTML.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from app.services.auth_service import AuthService
from app.services.worker_service import WorkerService

# Crear blueprint para páginas web
viewpages_bp = Blueprint('viewpages', __name__)


@viewpages_bp.route('/')
def home():
    """Página de inicio de Prontoa - Landing page."""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('viewpages.dashboard'))
    return render_template('index.html')


@viewpages_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de control principal - redirige según el tipo de usuario."""
    # Verificar si es un Worker
    if hasattr(current_user, 'worker_type'):
        # Es un trabajador, redirigir según su tipo
        if current_user.worker_type == 'planta':
            return redirect(url_for('viewpages.worker_kitchen'))
        elif current_user.worker_type == 'repartidor':
            return redirect(url_for('viewpages.worker_delivery'))
    
    # Es un User (owner/admin), mostrar dashboard principal
    return render_template('dashboard.html')


@viewpages_bp.route('/kpis')
@login_required
def kpis():
    """Página de KPIs y métricas de rendimiento (solo para owners/admins)."""
    # Solo los Users (owners) pueden acceder
    if hasattr(current_user, 'worker_type'):
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    return render_template('kpis.html')


@viewpages_bp.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario."""
    # Si es trabajador, redirigir a su perfil específico
    if hasattr(current_user, 'worker_type'):
        return redirect(url_for('viewpages.worker_profile'))
    
    return render_template('profile.html')


@viewpages_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro/crear cuenta."""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('viewpages.dashboard'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        full_name = request.form.get('fullName')
        phone = request.form.get('phone')
        business_name = request.form.get('businessName')
        business_type = request.form.get('businessType', 'restaurant')
        
        # Validaciones básicas
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('register.html')
        
        # Registrar usuario
        success, message, user = AuthService.register_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            business_name=business_name,
            business_type=business_type
        )
        
        if success:
            flash('Cuenta creada exitosamente. Por favor inicia sesión.', 'success')
            return redirect(url_for('viewpages.login'))
        else:
            flash(message, 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@viewpages_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('viewpages.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Autenticar usuario (devuelve 4 valores)
        success, message, user, user_type = AuthService.login_user_service(
            email=email,
            password=password,
            remember=remember
        )
        
        if success:
            flash('Inicio de sesión exitoso', 'success')
            # Redirigir según el tipo de usuario
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirigir según el tipo de usuario y worker_type
            if user_type == 'worker':
                if user.worker_type == 'planta':
                    return redirect(url_for('viewpages.worker_kitchen'))
                elif user.worker_type == 'repartidor':
                    return redirect(url_for('viewpages.worker_delivery'))
            
            # Por defecto, al dashboard (que redirigirá según tipo)
            return redirect(url_for('viewpages.dashboard'))
        else:
            flash(message, 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@viewpages_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario."""
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('viewpages.home'))


@viewpages_bp.route('/settings')
@login_required
def settings():
    """Página de configuraciones del sistema."""
    return render_template('settings.html')


# ==================== RUTAS DE TRABAJADOR ====================

@viewpages_bp.route('/worker-login')
def worker_login():
    """Página de login para trabajadores."""
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('viewpages.dashboard'))
    return render_template('worker_login.html')


@viewpages_bp.route('/worker/kitchen')
@login_required
def worker_kitchen():
    """Página de pedidos para trabajadores de cocina/planta."""
    # Verificar que sea un worker de tipo planta
    if not hasattr(current_user, 'worker_type'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    if current_user.worker_type != 'planta':
        flash('Esta página es solo para personal de cocina', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    return render_template('worker_kitchen.html')


@viewpages_bp.route('/worker/delivery')
@login_required
def worker_delivery():
    """Página de pedidos para repartidores."""
    # Verificar que sea un worker de tipo repartidor
    if not hasattr(current_user, 'worker_type'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    if current_user.worker_type != 'repartidor':
        flash('Esta página es solo para repartidores', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    return render_template('worker_delivery.html')


@viewpages_bp.route('/worker-orders')
@login_required
def worker_orders():
    """Página de pedidos asignados al trabajador (genérica)."""
    # Verificar que sea un worker
    if not hasattr(current_user, 'worker_type'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    # Redirigir a la página específica según el tipo
    if current_user.worker_type == 'planta':
        return redirect(url_for('viewpages.worker_kitchen'))
    elif current_user.worker_type == 'repartidor':
        return redirect(url_for('viewpages.worker_delivery'))
    
    return render_template('worker_orders.html')


@viewpages_bp.route('/worker-profile')
@login_required
def worker_profile():
    """Página de perfil del trabajador."""
    # Verificar que sea un worker
    if not hasattr(current_user, 'worker_type'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('viewpages.dashboard'))
    
    worker_stats = WorkerService.get_worker_statistics(current_user.id)
    return render_template('worker_profile.html', worker=current_user, worker_stats=worker_stats)
