"""
Servicio de gestión de trabajadores.
Maneja CRUD, asignación de pedidos y permisos.
"""
from datetime import datetime, timezone
from app.extensions import db
from app.data.models import Worker, Order, Business


class WorkerService:
    """Servicio para gestión de trabajadores."""
    
    @staticmethod
    def create_worker(business_id, email, password, full_name, phone, worker_type='planta'):
        """
        Crea un nuevo trabajador.
        
        Args:
            business_id: ID del negocio
            email: Email del trabajador
            password: Contraseña
            full_name: Nombre completo
            phone: Teléfono
            worker_type: Tipo de trabajador ('planta' o 'repartidor')
            
        Returns:
            tuple: (success: bool, message: str, worker: Worker)
        """
        try:
            # Verificar que el negocio existe
            business = Business.query.get(business_id)
            if not business:
                return False, 'Negocio no encontrado', None
            
            # Validar worker_type
            if worker_type not in ['planta', 'repartidor']:
                return False, 'Tipo de trabajador inválido. Debe ser "planta" o "repartidor"', None
            
            # Verificar email único
            if Worker.query.filter_by(email=email).first():
                return False, 'El email ya está registrado', None
            
            # Verificar teléfono único
            if Worker.query.filter_by(phone=phone).first():
                return False, 'El teléfono ya está registrado', None
            
            # Crear trabajador
            worker = Worker(
                business_id=business_id,
                email=email,
                full_name=full_name,
                phone=phone,
                worker_type=worker_type,
                is_active=True
            )
            worker.set_password(password)
            
            db.session.add(worker)
            db.session.commit()
            
            return True, 'Trabajador creado exitosamente', worker
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al crear trabajador: {str(e)}', None
    
    @staticmethod
    def get_all_workers(business_id, include_inactive=False):
        """
        Obtiene todos los trabajadores de un negocio.
        
        Args:
            business_id: ID del negocio
            include_inactive: Si incluir trabajadores inactivos
            
        Returns:
            list: Lista de trabajadores
        """
        try:
            query = Worker.query.filter_by(business_id=business_id)
            
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            workers = query.order_by(Worker.created_at.desc()).all()
            return workers
            
        except Exception as e:
            print(f"Error al obtener trabajadores: {e}")
            return []
    
    @staticmethod
    def get_worker_by_id(worker_id):
        """Obtiene un trabajador por ID."""
        return Worker.query.get(worker_id)
    
    @staticmethod
    def get_worker_by_email(email):
        """Obtiene un trabajador por email."""
        return Worker.query.filter_by(email=email).first()
    
    @staticmethod
    def update_worker(worker_id, **kwargs):
        """
        Actualiza datos de un trabajador.
        
        Args:
            worker_id: ID del trabajador
            **kwargs: Campos a actualizar
            
        Returns:
            tuple: (success: bool, message: str, worker: Worker)
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return False, 'Trabajador no encontrado', None
            
            # Validar worker_type si se proporciona
            if 'worker_type' in kwargs and kwargs['worker_type'] not in ['planta', 'repartidor']:
                return False, 'Tipo de trabajador inválido. Debe ser "planta" o "repartidor"', None
            
            # Actualizar campos permitidos
            allowed_fields = ['full_name', 'phone', 'worker_type', 'is_active']
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(worker, field):
                    setattr(worker, field, value)
            
            worker.updated_at = lambda: datetime.now(timezone.utc)
            db.session.commit()
            
            return True, 'Trabajador actualizado exitosamente', worker
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al actualizar trabajador: {str(e)}', None
    
    @staticmethod
    def change_password(worker_id, old_password, new_password):
        """
        Cambia la contraseña de un trabajador.
        
        Args:
            worker_id: ID del trabajador
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return False, 'Trabajador no encontrado'
            
            if not worker.check_password(old_password):
                return False, 'Contraseña actual incorrecta'
            
            worker.set_password(new_password)
            worker.updated_at = lambda: datetime.now(timezone.utc)
            db.session.commit()
            
            return True, 'Contraseña actualizada exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cambiar contraseña: {str(e)}'
    
    @staticmethod
    def deactivate_worker(worker_id):
        """
        Desactiva un trabajador (soft delete).
        
        Args:
            worker_id: ID del trabajador
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return False, 'Trabajador no encontrado'
            
            worker.is_active = False
            worker.updated_at = lambda: datetime.now(timezone.utc)
            db.session.commit()
            
            return True, 'Trabajador desactivado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al desactivar trabajador: {str(e)}'
    
    @staticmethod
    def delete_worker(worker_id):
        """
        Elimina permanentemente un trabajador.
        
        Args:
            worker_id: ID del trabajador
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return False, 'Trabajador no encontrado'
            
            db.session.delete(worker)
            db.session.commit()
            
            return True, 'Trabajador eliminado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al eliminar trabajador: {str(e)}'
    
    @staticmethod
    def assign_order_to_worker(order_id, worker_id):
        """
        Asigna un pedido a un trabajador.
        
        Args:
            order_id: ID del pedido
            worker_id: ID del trabajador
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            order = Order.query.get(order_id)
            worker = Worker.query.get(worker_id)
            
            if not order:
                return False, 'Pedido no encontrado'
            if not worker:
                return False, 'Trabajador no encontrado'
            
            # Verificar que el trabajador pertenece al negocio del pedido
            if order.business_id != worker.business_id:
                return False, 'El trabajador no pertenece a este negocio'
            
            # Asignar pedido
            if worker not in order.assigned_workers:
                order.assigned_workers.append(worker)
                db.session.commit()
                return True, 'Pedido asignado exitosamente'
            else:
                return False, 'El pedido ya está asignado a este trabajador'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al asignar pedido: {str(e)}'
    
    @staticmethod
    def unassign_order_from_worker(order_id, worker_id):
        """
        Desasigna un pedido de un trabajador.
        
        Args:
            order_id: ID del pedido
            worker_id: ID del trabajador
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            order = Order.query.get(order_id)
            worker = Worker.query.get(worker_id)
            
            if not order or not worker:
                return False, 'Pedido o trabajador no encontrado'
            
            if worker in order.assigned_workers:
                order.assigned_workers.remove(worker)
                db.session.commit()
                return True, 'Pedido desasignado exitosamente'
            else:
                return False, 'El pedido no está asignado a este trabajador'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al desasignar pedido: {str(e)}'
    
    @staticmethod
    def get_worker_assigned_orders(worker_id, status=None):
        """
        Obtiene los pedidos asignados a un trabajador.
        
        Args:
            worker_id: ID del trabajador
            status: Filtrar por estado (opcional)
            
        Returns:
            list: Lista de pedidos
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return []
            
            orders = worker.assigned_orders
            
            if status:
                orders = [o for o in orders if o.status == status]
            
            return sorted(orders, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            print(f"Error al obtener pedidos del trabajador: {e}")
            return []
    
    @staticmethod
    def get_worker_statistics(worker_id):
        """
        Obtiene estadísticas de un trabajador.
        
        Args:
            worker_id: ID del trabajador
            
        Returns:
            dict: Estadísticas del trabajador
        """
        try:
            worker = Worker.query.get(worker_id)
            if not worker:
                return {}
            
            total_orders = len(worker.assigned_orders)
            completed_orders = len([o for o in worker.assigned_orders if o.status in ['paid', 'closed']])
            preparing_orders = len([o for o in worker.assigned_orders if o.status == 'preparing'])
            ready_orders = len([o for o in worker.assigned_orders if o.status == 'ready'])
            
            return {
                'worker_id': worker.id,
                'full_name': worker.full_name,
                'total_orders_assigned': total_orders,
                'completed_orders': completed_orders,
                'preparing_orders': preparing_orders,
                'ready_orders': ready_orders,
                'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
                'last_login': worker.last_login.isoformat() if worker.last_login else None
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}
    
    @staticmethod
    def authenticate_worker(email, password):
        """
        Autentica un trabajador.
        
        Args:
            email: Email del trabajador
            password: Contraseña
            
        Returns:
            tuple: (success: bool, message: str, worker: Worker)
        """
        try:
            worker = Worker.query.filter_by(email=email).first()
            
            if not worker:
                return False, 'Credenciales inválidas', None
            
            if not worker.is_active:
                return False, 'La cuenta está desactivada', None
            
            if not worker.check_password(password):
                return False, 'Credenciales inválidas', None
            
            # Actualizar último login
            worker.last_login = lambda: datetime.now(timezone.utc)
            db.session.commit()
            
            return True, 'Autenticación exitosa', worker
            
        except Exception as e:
            return False, f'Error de autenticación: {str(e)}', None
