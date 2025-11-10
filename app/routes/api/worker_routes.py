"""
API Routes para trabajadores.
Endpoints para gestión de trabajadores y sus acciones.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.data.models import Worker, Order, Notification
from app.services.worker_service import WorkerService

worker_bp = Blueprint('worker_api', __name__, url_prefix='/api/workers')


# ==================== AUTENTICACIÓN ====================

@worker_bp.route('/login', methods=['POST'])
def worker_login():
    """
    Login de trabajador.
    
    POST /api/workers/login
    Body: {"email": "worker@example.com", "password": "123456"}
    """
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        success, message, worker = WorkerService.authenticate_worker(email, password)
        
        if not success:
            return jsonify({'error': message}), 401
        
        # Aquí deberías usar Flask-Login para el worker también
        # Por ahora retornamos los datos
        return jsonify({
            'message': message,
            'worker': worker.to_dict(),
            'business_id': worker.business_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en login: {str(e)}'}), 500


# ==================== CRUD DE TRABAJADORES (Solo Admin) ====================

@worker_bp.route('', methods=['POST'])
@login_required
def create_worker():
    """
    Crea un nuevo trabajador (solo dueño del negocio).
    
    POST /api/workers
    Body: {
        "email": "worker@example.com",
        "password": "123456",
        "full_name": "Juan Pérez",
        "phone": "+573001234567",
        "role": "worker"
    }
    """
    try:
        # Verificar que el usuario tiene negocio
        if not current_user.business:
            return jsonify({'error': 'No tienes un negocio registrado'}), 403
        
        data = request.json
        required_fields = ['email', 'password', 'full_name', 'phone']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        success, message, worker = WorkerService.create_worker(
            business_id=current_user.business.id,
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            phone=data['phone'],
            role=data.get('role', 'worker')
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'message': message,
            'worker': worker.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear trabajador: {str(e)}'}), 500


@worker_bp.route('', methods=['GET'])
@login_required
def get_all_workers():
    """
    Obtiene todos los trabajadores del negocio.
    
    GET /api/workers?include_inactive=false
    """
    try:
        if not current_user.business:
            return jsonify({'error': 'No tienes un negocio registrado'}), 403
        
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        workers = WorkerService.get_all_workers(
            business_id=current_user.business.id,
            include_inactive=include_inactive
        )
        
        return jsonify({
            'workers': [w.to_dict() for w in workers],
            'total': len(workers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener trabajadores: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>', methods=['GET'])
@login_required
def get_worker(worker_id):
    """
    Obtiene un trabajador por ID.
    
    GET /api/workers/123
    """
    try:
        worker = WorkerService.get_worker_by_id(worker_id)
        
        if not worker:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        # Verificar que el trabajador pertenece al negocio del usuario
        if worker.business_id != current_user.business.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        return jsonify({'worker': worker.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener trabajador: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>', methods=['PUT', 'PATCH'])
@login_required
def update_worker(worker_id):
    """
    Actualiza un trabajador.
    
    PUT /api/workers/123
    Body: {"full_name": "Juan Actualizado", "role": "supervisor"}
    """
    try:
        worker = WorkerService.get_worker_by_id(worker_id)
        
        if not worker:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        if worker.business_id != current_user.business.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        data = request.json
        success, message, updated_worker = WorkerService.update_worker(worker_id, **data)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'message': message,
            'worker': updated_worker.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al actualizar trabajador: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>', methods=['DELETE'])
@login_required
def delete_worker(worker_id):
    """
    Elimina un trabajador.
    
    DELETE /api/workers/123
    """
    try:
        worker = WorkerService.get_worker_by_id(worker_id)
        
        if not worker:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        if worker.business_id != current_user.business.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        success, message = WorkerService.delete_worker(worker_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al eliminar trabajador: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>/deactivate', methods=['POST'])
@login_required
def deactivate_worker(worker_id):
    """
    Desactiva un trabajador.
    
    POST /api/workers/123/deactivate
    """
    try:
        worker = WorkerService.get_worker_by_id(worker_id)
        
        if not worker:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        if worker.business_id != current_user.business.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        success, message = WorkerService.deactivate_worker(worker_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al desactivar trabajador: {str(e)}'}), 500


# ==================== ASIGNACIÓN DE PEDIDOS ====================

@worker_bp.route('/<int:worker_id>/assign-order', methods=['POST'])
@login_required
def assign_order(worker_id):
    """
    Asigna un pedido a un trabajador.
    
    POST /api/workers/123/assign-order
    Body: {"order_id": 456}
    """
    try:
        data = request.json
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'error': 'order_id es requerido'}), 400
        
        success, message = WorkerService.assign_order_to_worker(order_id, worker_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al asignar pedido: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>/unassign-order', methods=['POST'])
@login_required
def unassign_order(worker_id):
    """
    Desasigna un pedido de un trabajador.
    
    POST /api/workers/123/unassign-order
    Body: {"order_id": 456}
    """
    try:
        data = request.json
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'error': 'order_id es requerido'}), 400
        
        success, message = WorkerService.unassign_order_from_worker(order_id, worker_id)
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al desasignar pedido: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>/orders', methods=['GET'])
@login_required
def get_worker_orders(worker_id):
    """
    Obtiene los pedidos asignados a un trabajador.
    
    GET /api/workers/123/orders?status=preparing
    """
    try:
        status = request.args.get('status')
        
        orders = WorkerService.get_worker_assigned_orders(worker_id, status)
        
        return jsonify({
            'orders': [o.to_dict() for o in orders],
            'total': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener pedidos: {str(e)}'}), 500


@worker_bp.route('/<int:worker_id>/statistics', methods=['GET'])
@login_required
def get_worker_statistics(worker_id):
    """
    Obtiene estadísticas de un trabajador.
    
    GET /api/workers/123/statistics
    """
    try:
        stats = WorkerService.get_worker_statistics(worker_id)
        
        if not stats:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        return jsonify({'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500


# ==================== ACCIÓN DE TRABAJADOR: MARCAR LISTO ====================

@worker_bp.route('/mark-order-ready/<int:order_id>', methods=['POST'])
def mark_order_ready(order_id):
    """
    🎯 ENDPOINT PRINCIPAL: Trabajador marca un pedido como listo.
    
    POST /api/workers/mark-order-ready/123
    Body: {"worker_id": 456}
    
    Este es el endpoint que el trabajador usa con UN SOLO BOTÓN
    para cambiar el estado de "preparing" a "ready".
    """
    try:
        data = request.json
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return jsonify({'error': 'worker_id es requerido'}), 400
        
        # Obtener trabajador y pedido
        worker = WorkerService.get_worker_by_id(worker_id)
        order = Order.query.get(order_id)
        
        if not worker:
            return jsonify({'error': 'Trabajador no encontrado'}), 404
        
        if not order:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        # Verificar que el trabajador tiene permiso
        if not worker.can_mark_ready:
            return jsonify({'error': 'No tienes permiso para marcar pedidos como listos'}), 403
        
        # Verificar que el trabajador pertenece al negocio del pedido
        if order.business_id != worker.business_id:
            return jsonify({'error': 'Este pedido no pertenece a tu negocio'}), 403
        
        # Verificar que el pedido está en estado 'preparing'
        if order.status != 'preparing':
            return jsonify({
                'error': f'El pedido debe estar en estado "preparando". Estado actual: {order.status}'
            }), 400
        
        # Cambiar estado a 'ready'
        order.status = 'ready'
        order.ready_at = datetime.utcnow()
        
        # Calcular tiempo de preparación
        if order.accepted_at:
            delta = order.ready_at - order.accepted_at
            order.preparation_time_seconds = int(delta.total_seconds())
        
        db.session.commit()
        
        # 📱 Enviar notificación por WhatsApp (opcional)
        try:
            from app.services.whatsapp_service import WhatsAppService
            whatsapp_service = WhatsAppService(current_app.config)
            
            message = f"✅ ¡Tu pedido #{order.order_number} está listo para recoger/entregar!"
            whatsapp_service.send_message(
                to=order.customer.phone,
                message=message
            )
            notification_sent = True
        except Exception as e:
            current_app.logger.error(f"Error enviando WhatsApp: {e}")
            notification_sent = False
        
        # Crear notificación en sistema para el admin
        notification = Notification(
            user_id=order.business.user_id,
            title='Pedido Listo',
            message=f'El trabajador {worker.full_name} marcó el pedido #{order.order_number} como listo',
            notification_type='success',
            related_order_id=order.id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Pedido marcado como listo exitosamente',
            'order': order.to_dict(),
            'notification_sent': notification_sent,
            'preparation_time_seconds': order.preparation_time_seconds
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al marcar pedido como listo: {str(e)}'}), 500


# ==================== CAMBIO DE CONTRASEÑA ====================

@worker_bp.route('/change-password', methods=['POST'])
def change_worker_password():
    """
    Cambiar contraseña de trabajador.
    
    POST /api/workers/change-password
    Body: {
        "worker_id": 123,
        "old_password": "oldpass",
        "new_password": "newpass"
    }
    """
    try:
        data = request.json
        worker_id = data.get('worker_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not all([worker_id, old_password, new_password]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        success, message = WorkerService.change_password(
            worker_id, old_password, new_password
        )
        
        if not success:
            return jsonify({'error': message}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al cambiar contraseña: {str(e)}'}), 500
