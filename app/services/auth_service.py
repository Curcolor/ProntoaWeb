"""
Servicio de autenticación.
Maneja la lógica de usuarios, validación de credenciales y tokens.
"""

import secrets


class AuthService:
    """Servicio pseudo-backend para autenticación."""
    
    # Usuarios hardcodeados (sin BD)
    USERS = {
        'admin@prontoa.test': {
            'password': 'AdminPass123',
            'role': 'admin',
            'name': 'Administrador'
        },
        'worker@prontoa.test': {
            'password': 'WorkerPass123',
            'role': 'trabajador',
            'name': 'Trabajador'
        }
    }
    
    @staticmethod
    def validate_credentials(email, password):
        """
        Valida credenciales de usuario.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario
            
        Returns:
            dict or None: Datos del usuario si es válido, None si no
        """
        user_data = AuthService.USERS.get(email)
        if user_data and user_data['password'] == password:
            return {
                'email': email,
                'role': user_data['role'],
                'name': user_data['name'],
                'token': secrets.token_hex(16)
            }
        return None
    
    @staticmethod
    def get_user_by_email(email):
        """
        Obtiene datos del usuario por email.
        
        Args:
            email (str): Email del usuario
            
        Returns:
            dict or None: Datos del usuario si existe
        """
        return AuthService.USERS.get(email)
    
    @staticmethod
    def is_valid_role(role):
        """
        Valida si el rol existe en el sistema.
        
        Args:
            role (str): Rol a validar
            
        Returns:
            bool: True si es válido
        """
        valid_roles = ['admin', 'trabajador']
        return role in valid_roles
