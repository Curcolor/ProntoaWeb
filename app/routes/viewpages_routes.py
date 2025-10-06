"""
Blueprint para las páginas web de la interfaz de usuario.
Maneja las rutas que renderizan templates HTML.
"""

from flask import Blueprint, render_template

# Crear blueprint para páginas web
viewpages_bp = Blueprint('viewpages', __name__)


@viewpages_bp.route('/')
def home():
    """Página de inicio de Prontoa - Landing page."""
    return render_template('index.html')


@viewpages_bp.route('/dashboard')
def dashboard():
    """Panel de control principal con tablero Kanban de pedidos."""
    return render_template('dashboard.html')


@viewpages_bp.route('/kpis')
def kpis():
    """Página de KPIs y métricas de rendimiento."""
    return render_template('kpis.html')


@viewpages_bp.route('/profile')
def profile():
    """Página de perfil del usuario con información personal y métricas."""
    return render_template('profile.html')


@viewpages_bp.route('/register')
def register():
    """Página de registro/crear cuenta."""
    return render_template('register.html')


@viewpages_bp.route('/login')
def login():
    """Página de inicio de sesión."""
    return render_template('login.html')


@viewpages_bp.route('/settings')
def settings():
    """Página de configuraciones del sistema."""
    return render_template('settings.html')