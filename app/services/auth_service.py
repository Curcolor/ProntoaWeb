"""
Servicio de autenticación.
Maneja registro, login, logout y gestión de sesiones.
"""
from datetime import datetime
from flask import flash
from flask_login import login_user, logout_user
from app.extensions import db
from app.data.models import User, Business


class AuthService:
    """Servicio para autenticación de usuarios."""
    
    @staticmethod
    def register_user(email, password, full_name, phone, business_name, business_type):
        """
        Registra un nuevo usuario y su negocio.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            full_name: Nombre completo del usuario
            phone: Teléfono del usuario
            business_name: Nombre del negocio
            business_type: Tipo de negocio
            
        Returns:
            tuple: (success: bool, message: str, user: User)
        """
        try:
            # Verificar si el email ya existe
            if User.query.filter_by(email=email).first():
                return False, 'El email ya está registrado', None
            
            # Verificar si el teléfono ya existe
            if User.query.filter_by(phone=phone).first():
                return False, 'El teléfono ya está registrado', None
            
            # Crear nuevo usuario
            user = User(
                email=email,
                full_name=full_name,
                phone=phone
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Para obtener el ID del usuario
            
            # Crear el negocio asociado
            business = Business(
                user_id=user.id,
                name=business_name,
                business_type=business_type,
                whatsapp_number=phone  # Por defecto usar el mismo teléfono
            )
            
            db.session.add(business)
            db.session.commit()
            
            return True, 'Usuario registrado exitosamente', user
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al registrar usuario: {str(e)}', None
    
    @staticmethod
    def login_user_service(email, password, remember=False):
        """
        Autentica un usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            remember: Si se debe recordar la sesión
            
        Returns:
            tuple: (success: bool, message: str, user: User)
        """
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                return False, 'Email o contraseña incorrectos', None
            
            if not user.check_password(password):
                return False, 'Email o contraseña incorrectos', None
            
            if not user.is_active:
                return False, 'Tu cuenta ha sido desactivada', None
            
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Login con Flask-Login
            login_user(user, remember=remember)
            
            return True, 'Inicio de sesión exitoso', user
            
        except Exception as e:
            return False, f'Error al iniciar sesión: {str(e)}', None
    
    @staticmethod
    def logout_user_service():
        """
        Cierra la sesión del usuario actual.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            logout_user()
            return True, 'Sesión cerrada exitosamente'
        except Exception as e:
            return False, f'Error al cerrar sesión: {str(e)}'
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user: Usuario
            old_password: Contraseña antigua
            new_password: Nueva contraseña
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not user.check_password(old_password):
                return False, 'La contraseña actual es incorrecta'
            
            user.set_password(new_password)
            db.session.commit()
            
            return True, 'Contraseña cambiada exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cambiar contraseña: {str(e)}'
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            User o None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            User o None
        """
        return User.query.filter_by(email=email).first()
