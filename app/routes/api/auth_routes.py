"""
Blueprint de API para autenticación.
Maneja login, registro y gestión de sesiones vía API REST.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.auth_service import AuthService
from app.data.schemas import login_schema, register_schema
from marshmallow import ValidationError

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario vía API."""
    try:
        # Validar datos de entrada
        data = request.get_json()
        
        # Validación manual de confirmación de contraseña
        if data.get('password') != data.get('confirm_password'):
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }), 400
        
        validated_data = register_schema.load(data)
        
        # Registrar usuario
        success, message, user = AuthService.register_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data['phone'],
            business_name=validated_data['business_name'],
            business_type=validated_data['business_type']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Datos de entrada inválidos',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """Inicia sesión vía API."""
    try:
        data = request.get_json()
        validated_data = login_schema.load(data)
        
        success, message, user = AuthService.login_user_service(
            email=validated_data['email'],
            password=validated_data['password'],
            remember=validated_data.get('remember', False)
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Datos de entrada inválidos',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@auth_api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Cierra sesión vía API."""
    try:
        success, message = AuthService.logout_user_service()
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@auth_api_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obtiene información del usuario actual."""
    try:
        return jsonify({
            'success': True,
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500


@auth_api_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Cambia la contraseña del usuario actual."""
    try:
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Contraseña antigua y nueva son requeridas'
            }), 400
        
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'La nueva contraseña debe tener al menos 8 caracteres'
            }), 400
        
        success, message = AuthService.change_password(
            user=current_user,
            old_password=old_password,
            new_password=new_password
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500
