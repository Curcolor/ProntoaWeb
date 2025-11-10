"""
Blueprint para las páginas web de la interfaz de usuario.
Maneja las rutas que renderizan templates HTML.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from app.services.auth_service import AuthService

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
    """Panel de control principal con tablero Kanban de pedidos (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('dashboard.html')


@viewpages_bp.route('/kpis')
@login_required
def kpis():
    """Página de KPIs y métricas de rendimiento (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('kpis.html')


@viewpages_bp.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
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
        
        # Autenticar usuario
        success, message, user = AuthService.login_user_service(
            email=email,
            password=password,
            remember=remember
        )
        
        if success:
            flash('Inicio de sesión exitoso', 'success')
            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('viewpages.dashboard'))
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
