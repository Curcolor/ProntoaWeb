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