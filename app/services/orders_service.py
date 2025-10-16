"""
Servicio de gestión de pedidos.
Contiene lógica de negocio relacionada con pedidos.
"""


class OrdersService:
    """Servicio pseudo-backend para gestión de pedidos."""
    
    # Pedidos falsos (sin BD)
    # En producción, estos vendrían de una base de datos
    ORDERS = [
        {
            'id': 101,
            'customer': 'Cliente A',
            'items': '2x Arepa + 1x Jugo',
            'status': 'Recibido',
            'assigned_to': 'worker@prontoa.test',
            'created_at': '2024-01-15 10:30',
            'priority': 'normal'
        },
        {
            'id': 102,
            'customer': 'Cliente B',
            'items': '3x Empanada',
            'status': 'En Preparación',
            'assigned_to': 'worker@prontoa.test',
            'created_at': '2024-01-15 10:45',
            'priority': 'alta'
        },
        {
            'id': 103,
            'customer': 'Cliente C',
            'items': '1x Bandeja Paisa',
            'status': 'Listo',
            'assigned_to': 'worker@prontoa.test',
            'created_at': '2024-01-15 11:00',
            'priority': 'normal'
        }
    ]
    
    @staticmethod
    def get_all_orders():
        """
        Obtiene todos los pedidos.
        
        Returns:
            list: Lista de todos los pedidos
        """
        return OrdersService.ORDERS
    
    @staticmethod
    def get_orders_by_worker(worker_email):
        """
        Obtiene pedidos asignados a un trabajador específico.
        
        Args:
            worker_email (str): Email del trabajador
            
        Returns:
            list: Pedidos asignados al trabajador
        """
        return [
            order for order in OrdersService.ORDERS
            if order['assigned_to'] == worker_email
        ]
    
    @staticmethod
    def get_order_by_id(order_id):
        """
        Obtiene un pedido específico por ID.
        
        Args:
            order_id (int): ID del pedido
            
        Returns:
            dict or None: Pedido si existe
        """
        for order in OrdersService.ORDERS:
            if order['id'] == order_id:
                return order
        return None
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """
        Actualiza el estado de un pedido.
        
        Args:
            order_id (int): ID del pedido
            new_status (str): Nuevo estado
            
        Returns:
            bool: True si se actualizó, False si no existe
        """
        order = OrdersService.get_order_by_id(order_id)
        if order:
            order['status'] = new_status
            return True
        return False
    
    @staticmethod
    def get_orders_summary():
        """
        Obtiene resumen de estadísticas de pedidos.
        
        Returns:
            dict: Estadísticas de pedidos
        """
        total = len(OrdersService.ORDERS)
        completed = sum(1 for o in OrdersService.ORDERS if o['status'] == 'Listo')
        
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'high_priority': sum(1 for o in OrdersService.ORDERS if o['priority'] == 'alta')
        }
