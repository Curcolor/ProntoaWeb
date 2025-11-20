"""
Servicio de gestión de pedidos.
Maneja la creación, actualización y seguimiento de pedidos.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from flask import current_app
from app.extensions import db
from app.data.models import Order, OrderItem, Customer, Product, Business


class OrderService:
    """Servicio para gestión de pedidos."""
    
    @staticmethod
    def create_order(business_id, customer_phone, items_data, order_type='delivery', 
                    delivery_address=None, notes=None, customer_name=None):
        """
        Crea un nuevo pedido.
        
        Args:
            business_id: ID del negocio
            customer_phone: Teléfono del cliente
            items_data: Lista de ítems del pedido [{'product_id': 1, 'quantity': 2}, ...]
            order_type: Tipo de pedido (delivery, pickup)
            delivery_address: Dirección de entrega
            notes: Notas adicionales
            customer_name: Nombre del cliente
            
        Returns:
            tuple: (success: bool, message: str, order: Order)
        """
        try:
            # Obtener o crear cliente
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if not customer:
                customer = Customer(
                    phone=customer_phone,
                    name=customer_name or 'Cliente'
                )
                db.session.add(customer)
                db.session.flush()
            
            # Generar número de pedido único con reintentos
            order = None
            last_error = None
            for _ in range(5):
                try:
                    order_number = OrderService._generate_order_number(business_id)
                    order = Order(
                        order_number=order_number,
                        business_id=business_id,
                        customer_id=customer.id,
                        status='received',
                        order_type=order_type,
                        delivery_address=delivery_address,
                        notes=notes,
                        total_amount=0  # Se calculará después
                    )
                    db.session.add(order)
                    db.session.flush()
                    break
                except IntegrityError as err:
                    db.session.rollback()
                    last_error = err
                    continue
            if order is None:
                return False, f'Error generando número de pedido: {last_error}', None
            
            # Agregar ítems del pedido
            total_amount = 0
            for item_data in items_data:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    db.session.rollback()
                    return False, f'Producto {item_data["product_id"]} no encontrado', None
                
                if not product.is_available:
                    db.session.rollback()
                    return False, f'Producto {product.name} no está disponible', None
                
                quantity = item_data['quantity']
                unit_price = product.price
                subtotal = unit_price * quantity
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                    notes=item_data.get('notes')
                )
                
                db.session.add(order_item)
                total_amount += subtotal
            
            # Actualizar total del pedido
            order.total_amount = total_amount
            
            # Actualizar contador de pedidos del cliente
            customer.total_orders += 1
            
            db.session.commit()
            
            return True, 'Pedido creado exitosamente', order
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al crear pedido: {str(e)}', None
    
    @staticmethod
    def update_order_status(order_id, new_status, user_id=None):
        """
        Actualiza el estado de un pedido.
        
        Args:
            order_id: ID del pedido
            new_status: Nuevo estado del pedido
            user_id: ID del usuario que realiza la actualización
            
        Returns:
            tuple: (success: bool, message: str, order: Order)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, 'Pedido no encontrado', None
            
            old_status = order.status
            order.status = new_status
            now = datetime.now(timezone.utc)
            order.updated_at = now
            
            # Actualizar tiempos según el estado
            if new_status == 'preparing':
                if not order.accepted_at:
                    order.accepted_at = now
                if not order.preparing_at:
                    order.preparing_at = now
                if not order.response_time_seconds:
                    response_seconds = OrderService._seconds_between(order.created_at, order.accepted_at)
                    if response_seconds is not None:
                        order.response_time_seconds = response_seconds

            elif new_status == 'ready':
                if not order.ready_at:
                    order.ready_at = now
                if not order.preparation_time_seconds:
                    prep_seconds = OrderService._seconds_between(order.accepted_at, order.ready_at)
                    if prep_seconds is not None:
                        order.preparation_time_seconds = prep_seconds

            elif new_status in ['sent', 'out_for_delivery']:
                if not order.sent_at:
                    order.sent_at = now

            elif new_status == 'paid':
                if not order.paid_at:
                    order.paid_at = now

            if new_status in ['delivered', 'closed'] and not order.delivered_at:
                order.delivered_at = now
            
            db.session.commit()
            
            OrderService._notify_status_change(order, old_status, new_status)
            return True, f'Pedido actualizado de {old_status} a {new_status}', order
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al actualizar pedido: {str(e)}', None
    
    @staticmethod
    def get_orders_by_business(business_id, status=None, limit=None, offset=0):
        """
        Obtiene los pedidos de un negocio.
        
        Args:
            business_id: ID del negocio
            status: Filtrar por estado (opcional)
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            list: Lista de pedidos
        """
        query = Order.query.filter_by(business_id=business_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Order.created_at.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    def get_order_by_number(order_number):
        """
        Obtiene un pedido por su número.
        
        Args:
            order_number: Número del pedido
            
        Returns:
            Order o None
        """
        return Order.query.filter_by(order_number=order_number).first()
    
    @staticmethod
    def get_orders_by_status_count(business_id):
        """
        Cuenta los pedidos por estado para un negocio.
        
        Args:
            business_id: ID del negocio
            
        Returns:
            dict: Diccionario con conteos por estado
        """
        counts = db.session.query(
            Order.status,
            func.count(Order.id)
        ).filter_by(business_id=business_id).group_by(Order.status).all()
        
        return {status: count for status, count in counts}
    
    @staticmethod
    def get_today_orders_count(business_id):
        """
        Obtiene el conteo de pedidos del día.
        
        Args:
            business_id: ID del negocio
            
        Returns:
            int: Cantidad de pedidos del día
        """
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start
            )
        ).count()
    
    @staticmethod
    def get_average_response_time(business_id, days=30):
        """
        Calcula el tiempo promedio de respuesta.
        
        Args:
            business_id: ID del negocio
            days: Días a considerar en el cálculo
            
        Returns:
            float: Tiempo promedio en minutos
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        avg_seconds = db.session.query(
            func.avg(Order.response_time_seconds)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.response_time_seconds.isnot(None)
            )
        ).scalar()
        
        return round(avg_seconds / 60, 1) if avg_seconds else 0
    
    @staticmethod
    def get_total_sales_today(business_id):
        """
        Obtiene el total de ventas del día.
        
        Args:
            business_id: ID del negocio
            
        Returns:
            float: Total de ventas
        """
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        total = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start,
                Order.status.notin_(['cancelled'])
            )
        ).scalar()
        
        return float(total) if total else 0
    
    @staticmethod
    def _generate_order_number(business_id):
        """
        Genera un número único de pedido.
        
        Args:
            business_id: ID del negocio
            
        Returns:
            str: Número de pedido único
        """
        today = datetime.now(timezone.utc)
        prefix = f"{business_id}{today.strftime('%Y%m%d')}"
        
        # Contar pedidos existentes y buscar huecos disponibles
        existing_numbers = [o.order_number for o in Order.query.with_entities(Order.order_number)
                             .filter(Order.order_number.like(f"{prefix}%"))
                             .order_by(Order.order_number).all()]
        existing_set = set(existing_numbers)
        for suffix in range(1, 10000):
            candidate = f"{prefix}{suffix:04d}"
            if candidate not in existing_set:
                return candidate
        raise ValueError('No hay números de pedido disponibles para hoy')

    @staticmethod
    def _ensure_timezone(dt):
        """Garantiza que un datetime tenga zona horaria UTC para poder restarlo."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _seconds_between(start, end):
        start_aware = OrderService._ensure_timezone(start)
        end_aware = OrderService._ensure_timezone(end)
        if not start_aware or not end_aware:
            return None
        return int((end_aware - start_aware).total_seconds())

    @staticmethod
    def _notify_status_change(order, old_status, new_status):
        if not order or old_status == new_status:
            return
        customer = order.customer
        if not customer or not customer.phone:
            return
        phone = customer.phone
        try:
            if phone.startswith('tg:'):
                from app.services.telegram_service import TelegramService
                TelegramService().send_order_status_update(order, new_status)
        except Exception as exc:
            current_app = None
            try:
                from flask import current_app as flask_current_app
                current_app = flask_current_app
            except Exception:
                pass
            if current_app:
                current_app.logger.error(f"Error enviando notificación de estado: {exc}")
    
    @staticmethod
    def cancel_order(order_id, reason=None):
        """
        Cancela un pedido.
        
        Args:
            order_id: ID del pedido
            reason: Razón de la cancelación
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, 'Pedido no encontrado'
            
            if order.status in ['paid', 'closed']:
                return False, 'No se puede cancelar un pedido pagado o cerrado'
            
            order.status = 'cancelled'
            if reason:
                order.notes = f"{order.notes}\nCancelado: {reason}" if order.notes else f"Cancelado: {reason}"
            
            db.session.commit()
            
            return True, 'Pedido cancelado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cancelar pedido: {str(e)}'
