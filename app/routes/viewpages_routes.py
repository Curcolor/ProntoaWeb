"""
Blueprint para las páginas web de la interfaz de usuario.
Maneja las rutas que renderizan templates HTML.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import AuthService, OrdersService, WorkersService

# Crear blueprint para páginas web
viewpages_bp = Blueprint('viewpages', __name__)


@viewpages_bp.route('/')
def home():
    """Página de inicio de Prontoa - Landing page."""
    return render_template('index.html')


@viewpages_bp.route('/dashboard')
def dashboard():
    """Panel de control principal con tablero Kanban de pedidos (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('dashboard.html')


@viewpages_bp.route('/kpis')
def kpis():
    """Página de KPIs y métricas de rendimiento (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('kpis.html')


@viewpages_bp.route('/profile')
def profile():
    """Página de perfil del usuario (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('profile.html')


@viewpages_bp.route('/register')
def register():
    """Página de registro/crear cuenta."""
    return render_template('register.html')


@viewpages_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión con dos usuarios: admin y trabajador."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validar credenciales usando el servicio
        user_data = AuthService.validate_credentials(email, password)
        if user_data:
            session['user'] = user_data
            session.permanent = True
            
            if user_data['role'] == 'admin':
                return redirect(url_for('viewpages.dashboard'))
            else:  # trabajador
                return redirect(url_for('viewpages.worker_orders'))
        else:
            error = 'Credenciales inválidas'
            return render_template('login.html', error=error)
    
    return render_template('login.html')


@viewpages_bp.route('/settings')
def settings():
    """Página de configuraciones del sistema (solo admin)."""
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return redirect(url_for('viewpages.login'))
    return render_template('settings.html')


@viewpages_bp.route('/logout')
def logout():
    """Cierra sesión."""
    session.clear()
    return redirect(url_for('viewpages.login'))


@viewpages_bp.route('/worker/orders')
def worker_orders():
    """Pantalla de pedidos para trabajador."""
    user = session.get('user')
    if not user or user.get('role') != 'trabajador':
        return redirect(url_for('viewpages.login'))
    
    # Obtener pedidos del trabajador usando el servicio
    orders = OrdersService.get_orders_by_worker(user.get('email'))
    return render_template('worker_orders.html', orders=orders)


@viewpages_bp.route('/worker/profile')
def worker_profile():
    """Perfil del trabajador."""
    user = session.get('user')
    if not user or user.get('role') != 'trabajador':
        return redirect(url_for('viewpages.login'))
    
    # Obtener datos del trabajador usando el servicio
    worker_data = WorkersService.get_worker_profile(user.get('email'))
    
    return render_template('worker_profile.html', worker=worker_data)