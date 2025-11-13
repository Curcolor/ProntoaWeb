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
        
        # Contar pedidos por estado
        by_status = {
            'received': 0,
            'preparing': 0,
            'ready': 0,
            'sent': 0,
            'paid': 0,
            'closed': 0
        }
        
        for order in orders:
            if order.status in by_status:
                by_status[order.status] += 1
        
        return jsonify({
            'success': True,
            'orders': orders_schema.dump(orders),
            'total': len(orders),
            'by_status': by_status
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


# ==================== ENDPOINTS PARA TRABAJADORES ====================

# ============================================================
# ENDPOINTS PARA TRABAJADORES EN PLANTA
# ============================================================

@orders_api_bp.route('/<int:order_id>/accept-to-preparing', methods=['POST'])
@login_required
def accept_to_preparing(order_id):
    """Acepta un pedido recibido y lo pasa a preparación (trabajador en planta)."""
    try:
        from app.data.models import Order, Worker
        from datetime import datetime, timezone
        from app.extensions import db
        
        # Verificar que sea trabajador en planta
        if not isinstance(current_user, Worker) or current_user.worker_type != 'planta':
            return jsonify({
                'success': False,
                'message': 'Solo trabajadores en planta pueden aceptar pedidos'
            }), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        if order.status != 'received':
            return jsonify({
                'success': False,
                'message': f'El pedido debe estar en "recibido" (actualmente: {order.status})'
            }), 400
        
        # Cambiar de received → preparing
        order.status = 'preparing'
        order.accepted_at = lambda: datetime.now(timezone.utc)()
        
        # Calcular tiempo de respuesta
        if order.created_at:
            time_diff = order.accepted_at - order.created_at
            order.response_time_seconds = int(time_diff.total_seconds())
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido aceptado y pasado a preparación',
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error aceptando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>/mark-ready', methods=['POST'])
@login_required
def mark_order_ready(order_id):
    """Marca un pedido como listo (trabajador en planta)."""
    try:
        from app.data.models import Order, Worker
        from app.services.whatsapp_service import WhatsAppService
        from datetime import datetime, timezone
        from app.extensions import db
        
        # Verificar que sea trabajador en planta
        if not isinstance(current_user, Worker) or current_user.worker_type != 'planta':
            return jsonify({
                'success': False,
                'message': 'Solo trabajadores en planta pueden marcar pedidos como listos'
            }), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        if order.status != 'preparing':
            return jsonify({
                'success': False,
                'message': f'El pedido debe estar en preparación (actualmente: {order.status})'
            }), 400
        
        # Cambiar de preparing → ready
        order.status = 'ready'
        order.ready_at = lambda: datetime.now(timezone.utc)()
        
        # Calcular tiempo de preparación
        if order.accepted_at:
            time_diff = order.ready_at - order.accepted_at
            order.preparation_time_seconds = int(time_diff.total_seconds())
        
        db.session.commit()
        
        # Enviar notificación WhatsApp al cliente
        notification_sent = False
        try:
            if order.customer and order.customer.phone:
                whatsapp_service = WhatsAppService()
                whatsapp_service.send_order_ready_notification(
                    customer_phone=order.customer.phone,
                    order_number=order.order_number,
                    order_type=order.order_type
                )
                notification_sent = True
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Pedido marcado como listo',
            'order': order_schema.dump(order),
            'notification_sent': notification_sent
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error marcando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>/cancel-to-previous', methods=['POST'])
@login_required
def cancel_to_previous(order_id):
    """Cancela y devuelve al estado anterior (trabajadores)."""
    try:
        from app.data.models import Order, Worker
        from app.extensions import db
        
        # Verificar que sea trabajador
        if not isinstance(current_user, Worker):
            return jsonify({
                'success': False,
                'message': 'Solo trabajadores pueden cancelar pedidos'
            }), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        # Mapa de cancelaciones (estado_actual → estado_anterior)
        cancel_map = {
            'preparing': 'received',
            'ready': 'preparing',
            'sent': 'ready',
            'paid': 'sent'
        }
        
        if order.status not in cancel_map:
            return jsonify({
                'success': False,
                'message': f'No se puede cancelar un pedido en estado: {order.status}'
            }), 400
        
        previous_status = cancel_map[order.status]
        order.status = previous_status
        
        # Limpiar timestamps según el nuevo estado
        if previous_status == 'received':
            order.accepted_at = None
            order.response_time_seconds = None
        elif previous_status == 'preparing':
            order.ready_at = None
            order.preparation_time_seconds = None
        elif previous_status == 'ready':
            order.delivered_at = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pedido devuelto a {previous_status}',
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error cancelando pedido: {str(e)}'
        }), 500


# ============================================================
# ENDPOINTS PARA TRABAJADORES REPARTIDORES
# ============================================================

@orders_api_bp.route('/<int:order_id>/accept-to-sent', methods=['POST'])
@login_required
def accept_to_sent(order_id):
    """Acepta un pedido listo para envío (trabajador repartidor)."""
    try:
        from app.data.models import Order, Worker
        from datetime import datetime, timezone
        from app.extensions import db
        
        # Verificar que sea trabajador repartidor
        if not isinstance(current_user, Worker) or current_user.worker_type != 'repartidor':
            return jsonify({
                'success': False,
                'message': 'Solo repartidores pueden aceptar pedidos para envío'
            }), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        if order.status != 'ready':
            return jsonify({
                'success': False,
                'message': f'El pedido debe estar listo (actualmente: {order.status})'
            }), 400
        
        # Cambiar de ready → sent
        order.status = 'sent'
        order.delivered_at = lambda: datetime.now(timezone.utc)()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido aceptado para envío',
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error aceptando pedido: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>/mark-paid', methods=['POST'])
@login_required
def mark_order_paid(order_id):
    """Marca un pedido como pagado y lo cierra automáticamente (trabajador repartidor)."""
    try:
        from app.data.models import Order, Worker
        from datetime import datetime, timezone
        from app.extensions import db
        
        # Verificar que sea trabajador repartidor
        if not isinstance(current_user, Worker) or current_user.worker_type != 'repartidor':
            return jsonify({
                'success': False,
                'message': 'Solo repartidores pueden marcar pedidos como pagados'
            }), 403
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No autorizado'
            }), 403
        
        if order.status != 'sent':
            return jsonify({
                'success': False,
                'message': f'El pedido debe estar enviado (actualmente: {order.status})'
            }), 400
        
        # Cambiar de sent → paid → closed automáticamente
        order.status = 'closed'  # Va directo a closed
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido marcado como pagado y cerrado',
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error marcando pedido como pagado: {str(e)}'
        }), 500


# ============================================================
# ENDPOINTS LEGACY (mantener por compatibilidad)
# ============================================================

@orders_api_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order_worker(order_id):
    """LEGACY: Redirige al nuevo endpoint de cancelación."""
    return cancel_to_previous(order_id)


# ==================== ENDPOINTS PARA TRABAJADORES ====================

@orders_api_bp.route('/worker/kitchen', methods=['GET'])
@login_required
def get_kitchen_orders():
    """
    Obtiene pedidos para trabajadores de cocina.
    Estados: received, preparing, ready
    """
    try:
        # Verificar que sea un trabajador
        if not hasattr(current_user, 'worker_type'):
            return jsonify({
                'success': False,
                'message': 'Acceso solo para trabajadores'
            }), 403
        
        # Verificar que sea trabajador de cocina
        if current_user.worker_type != 'planta':
            return jsonify({
                'success': False,
                'message': 'Acceso solo para trabajadores de cocina'
            }), 403
        
        # Obtener pedidos en estados relevantes para cocina
        business_id = current_user.business_id
        
        received_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='received'
        )
        
        preparing_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='preparing'
        )
        
        ready_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='ready'
        )
        
        # Combinar todos los pedidos
        all_orders = received_orders + preparing_orders + ready_orders
        
        # Serializar con información completa
        orders_data = []
        for order in all_orders:
            order_dict = order_schema.dump(order)
            # Agregar información del cliente
            if order.customer:
                # Customers store name as `name`; fall back to `full_name` if ever present
                customer_name = getattr(order.customer, 'name', None) or getattr(order.customer, 'full_name', None) or 'Cliente'
                order_dict['customer_name'] = customer_name
                order_dict['customer_phone'] = order.customer.phone
            # Agregar items
            order_dict['items'] = [
                {
                    'product_name': item.product.name if item.product else 'Producto',
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.subtotal)
                }
                for item in order.items
            ]
            orders_data.append(order_dict)
        
        return jsonify({
            'success': True,
            'orders': orders_data,
            'total': len(orders_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo pedidos de cocina: {str(e)}'
        }), 500


@orders_api_bp.route('/worker/delivery', methods=['GET'])
@login_required
def get_delivery_orders():
    """
    Obtiene pedidos para repartidores.
    Estados: ready, sent, paid
    """
    try:
        # Verificar que sea un trabajador
        if not hasattr(current_user, 'worker_type'):
            return jsonify({
                'success': False,
                'message': 'Acceso solo para trabajadores'
            }), 403
        
        # Verificar que sea repartidor
        if current_user.worker_type != 'repartidor':
            return jsonify({
                'success': False,
                'message': 'Acceso solo para repartidores'
            }), 403
        
        # Obtener pedidos en estados relevantes para repartidor
        business_id = current_user.business_id
        
        ready_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='ready'
        )
        
        sent_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='sent'
        )
        
        paid_orders = OrderService.get_orders_by_business(
            business_id=business_id,
            status='paid'
        )
        
        # Combinar todos los pedidos
        all_orders = ready_orders + sent_orders + paid_orders
        
        # Serializar con información completa
        orders_data = []
        for order in all_orders:
            order_dict = order_schema.dump(order)
            # Agregar información del cliente
            if order.customer:
                customer_name = getattr(order.customer, 'name', None) or getattr(order.customer, 'full_name', None) or 'Cliente'
                order_dict['customer_name'] = customer_name
                order_dict['customer_phone'] = order.customer.phone
            # Agregar dirección de entrega
            order_dict['delivery_address'] = order.delivery_address or 'No especificada'
            # Agregar items (opcional para repartidor, pero útil)
            order_dict['items'] = [
                {
                    'product_name': item.product.name if item.product else 'Producto',
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal)
                }
                for item in order.items
            ]
            orders_data.append(order_dict)
        
        return jsonify({
            'success': True,
            'orders': orders_data,
            'total': len(orders_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo pedidos de entrega: {str(e)}'
        }), 500


@orders_api_bp.route('/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status_worker(order_id):
    """
    Actualiza el estado de un pedido (para trabajadores).
    Body: { "status": "preparing|ready|sent|paid" }
    """
    try:
        # Verificar que sea un trabajador
        if not hasattr(current_user, 'worker_type'):
            return jsonify({
                'success': False,
                'message': 'Acceso solo para trabajadores'
            }), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Estado requerido'
            }), 400
        
        # Obtener el pedido
        from app.data.models import Order
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        # Verificar que el pedido sea del negocio del trabajador
        if order.business_id != current_user.business_id:
            return jsonify({
                'success': False,
                'message': 'No tienes permiso para este pedido'
            }), 403
        
        # Validar transiciones según el tipo de trabajador
        if current_user.worker_type == 'planta':
            # Cocina puede: received → preparing, preparing → ready
            allowed_transitions = {
                'received': ['preparing'],
                'preparing': ['ready']
            }
        elif current_user.worker_type == 'repartidor':
            # Repartidor puede: ready → sent, sent → paid
            allowed_transitions = {
                'ready': ['sent'],
                'sent': ['paid']
            }
        else:
            return jsonify({
                'success': False,
                'message': 'Tipo de trabajador no válido'
            }), 403
        
        # Verificar transición válida
        current_status = order.status
        if current_status not in allowed_transitions:
            return jsonify({
                'success': False,
                'message': f'No puedes cambiar pedidos en estado {current_status}'
            }), 400
        
        if new_status not in allowed_transitions[current_status]:
            return jsonify({
                'success': False,
                'message': f'Transición no permitida: {current_status} → {new_status}'
            }), 400
        
        # Actualizar el estado
        from datetime import datetime, timezone
        from app.extensions import db
        
        order.status = new_status
        order.updated_at = datetime.now(timezone.utc)
        
        # Actualizar campos específicos según el estado
        if new_status == 'preparing':
            order.preparing_at = datetime.now(timezone.utc)
        elif new_status == 'ready':
            order.ready_at = datetime.now(timezone.utc)
        elif new_status == 'sent':
            order.sent_at = datetime.now(timezone.utc)
        elif new_status == 'paid':
            order.paid_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pedido actualizado a {new_status}',
            'order': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error actualizando pedido: {str(e)}'
        }), 500
