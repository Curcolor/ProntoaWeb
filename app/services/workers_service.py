"""
Servicio de gestión de trabajadores.
Contiene lógica de negocio relacionada con trabajadores.
"""


class WorkersService:
    """Servicio pseudo-backend para gestión de trabajadores."""
    
    # Datos de trabajadores (sin BD)
    # En producción, estos vendrían de una base de datos
    WORKERS = {
        'worker@prontoa.test': {
            'name': 'Trabajador',
            'empresa': 'Panedería de Alexis TEST',
            'email': 'worker@prontoa.test',
            'phone': '+57 300 123 4567',
            'status': 'Activo',
            'joined': '15 de Enero, 2024',
            'total_orders': 237,
            'completed_orders': 235,
            'average_time': '4.2 minutos',
            'satisfaction': '98%'
        },
        'admin@prontoa.test': {
            'name': 'Administrador',
            'empresa': 'Panedería de Alexis TEST',
            'email': 'admin@prontoa.test',
            'phone': '+57 300 987 6543',
            'status': 'Activo',
            'joined': '01 de Enero, 2024',
            'total_orders': 0,
            'completed_orders': 0,
            'average_time': '-',
            'satisfaction': '-'
        }
    }
    
    @staticmethod
    def get_worker_profile(email):
        """
        Obtiene el perfil de un trabajador.
        
        Args:
            email (str): Email del trabajador
            
        Returns:
            dict or None: Datos del trabajador si existe
        """
        return WorkersService.WORKERS.get(email)
    
    @staticmethod
    def get_all_workers():
        """
        Obtiene todos los trabajadores.
        
        Returns:
            list: Lista de trabajadores
        """
        return list(WorkersService.WORKERS.values())
    
    @staticmethod
    def update_worker_stats(email, stats):
        """
        Actualiza estadísticas de un trabajador.
        
        Args:
            email (str): Email del trabajador
            stats (dict): Nuevas estadísticas
            
        Returns:
            bool: True si se actualizó, False si no existe
        """
        worker = WorkersService.get_worker_profile(email)
        if worker:
            worker.update(stats)
            return True
        return False
    
    @staticmethod
    def get_worker_statistics(email):
        """
        Obtiene estadísticas específicas de un trabajador.
        
        Args:
            email (str): Email del trabajador
            
        Returns:
            dict or None: Estadísticas del trabajador
        """
        worker = WorkersService.get_worker_profile(email)
        if worker:
            return {
                'total_orders': worker['total_orders'],
                'completed_orders': worker['completed_orders'],
                'average_time': worker['average_time'],
                'satisfaction': worker['satisfaction']
            }
        return None
