"""
Servicio de autenticación.
Maneja registro, login, logout y gestión de sesiones.
"""
from datetime import datetime, timezone
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
        Autentica un usuario o trabajador.
        
        Args:
            email: Email del usuario/trabajador
            password: Contraseña
            remember: Si se debe recordar la sesión
            
        Returns:
            tuple: (success: bool, message: str, user: User|Worker, user_type: str)
        """
        try:
            # Primero buscar en Users (admin/owners)
            user = User.query.filter_by(email=email).first()
            
            if user:
                if not user.check_password(password):
                    return False, 'Email o contraseña incorrectos', None, None
                
                if not user.is_active:
                    return False, 'Tu cuenta ha sido desactivada', None, None
                
                # Login con Flask-Login primero
                login_user(user, remember=remember)
                
                # Actualizar último login después del login
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                
                return True, 'Inicio de sesión exitoso', user, 'user'
            
            # Si no es User, buscar en Workers
            from app.data.models import Worker
            worker = Worker.query.filter_by(email=email).first()
            
            if worker:
                if not worker.check_password(password):
                    return False, 'Email o contraseña incorrectos', None, None
                
                if not worker.is_active:
                    return False, 'Tu cuenta ha sido desactivada', None, None
                
                # Login con Flask-Login primero
                login_user(worker, remember=remember)
                
                # Actualizar último login después del login
                worker.last_login = datetime.now(timezone.utc)
                db.session.commit()
                
                return True, 'Inicio de sesión exitoso', worker, 'worker'
            
            # No encontrado en ninguna tabla
            return False, 'Email o contraseña incorrectos', None, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al iniciar sesión: {str(e)}', None, None
    
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
    
    @staticmethod
    def update_user_name(user, new_name):
        """
        Actualiza el nombre completo del usuario.
        
        Args:
            user: Usuario
            new_name: Nuevo nombre completo
        """
        if not new_name or not new_name.strip():
            return False, 'El nombre no puede estar vacío'

        cleaned_name = new_name.strip()

        try:
            user.full_name = cleaned_name
            db.session.commit()
            return True, 'Nombre actualizado correctamente'
        except Exception as e:
            db.session.rollback()
            return False, f'Error al actualizar nombre: {str(e)}'