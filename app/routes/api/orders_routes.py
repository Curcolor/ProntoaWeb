"""
Blueprint de API para gestión de pedidos.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.order_service import OrderService
from app.data.schemas import order_schema, orders_schema, order_create_schema, order_update_schema
from marshmallow import ValidationError

orders_api_bp = Blueprint('orders_api', __name__, url_prefix='/api/orders')


@orders_api_bp.route('/', methods=['GET'])
@login_required
def get_orders():
    """Obtiene los pedidos del negocio del usuario actual."""
    try:
        # Verificar que el usuario tenga un negocio
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        # Parámetros de consulta
        status = request.args.get('status')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        orders = OrderService.get_orders_by_business(
            business_id=current_user.business.id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'orders': orders_schema.dump(orders),
            'total': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo pedidos: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Obtiene un pedido específico."""
    try:
        from app.data.models import Order
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        # Verificar que el pedido pertenezca al negocio del usuario
        if order.business_id != current_user.business.id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        return jsonify({
            'success': True,
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/', methods=['POST'])
@login_required
def create_order():
    """Crea un nuevo pedido."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        data = request.get_json()
        validated_data = order_create_schema.load(data)
        
        success, message, order = OrderService.create_order(
            business_id=current_user.business.id,
            customer_phone=validated_data['customer_phone'],
            items_data=validated_data['items'],
            order_type=validated_data.get('order_type', 'delivery'),
            delivery_address=validated_data.get('delivery_address'),
            notes=validated_data.get('notes'),
            customer_name=validated_data.get('customer_name')
        )
        
        if success:
            # Enviar confirmación por WhatsApp
            try:
                from app.services.whatsapp_service import WhatsAppService
                whatsapp = WhatsAppService()
                whatsapp.send_order_confirmation(order)
            except Exception as e:
                # Log error pero no fallar la creación del pedido
                pass
            
            return jsonify({
                'success': True,
                'message': message,
                'order': order_schema.dump(order)
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
            'message': f'Error creando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>', methods=['PATCH'])
@login_required
def update_order(order_id):
    """Actualiza un pedido."""
    try:
        from app.data.models import Order
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business.id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        data = request.get_json()
        validated_data = order_update_schema.load(data)
        
        new_status = validated_data.get('status')
        
        if new_status:
            success, message, updated_order = OrderService.update_order_status(
                order_id=order_id,
                new_status=new_status,
                user_id=current_user.id
            )
            
            if success:
                # Enviar notificación según el estado
                try:
                    from app.services.whatsapp_service import WhatsAppService
                    whatsapp = WhatsAppService()
                    
                    if new_status == 'ready':
                        whatsapp.send_order_ready(updated_order)
                    elif new_status in ['sent', 'delivered']:
                        whatsapp.send_order_delivered(updated_order)
                except:
                    pass
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'order': order_schema.dump(updated_order)
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        
        return jsonify({
            'success': False,
            'message': 'No hay campos para actualizar'
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
            'message': f'Error actualizando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancela un pedido."""
    try:
        from app.data.models import Order
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business.id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        data = request.get_json()
        reason = data.get('reason')
        
        success, message = OrderService.cancel_order(order_id, reason)
        
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
            'message': f'Error cancelando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/by-status', methods=['GET'])
@login_required
def get_orders_by_status():
    """Obtiene conteo de pedidos por estado."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        counts = OrderService.get_orders_by_status_count(current_user.business.id)
        
        return jsonify({
            'success': True,
            'counts': counts
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo conteos: {str(e)}'
        }), 500


@orders_api_bp.route('/by-number/<string:order_number>', methods=['GET'])
@login_required
def get_order_by_number(order_number):
    """Obtiene un pedido por su número."""
    try:
        order = OrderService.get_order_by_number(order_number)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business.id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        return jsonify({
            'success': True,
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo pedido: {str(e)}'
        }), 500
