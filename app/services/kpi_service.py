"""
Servicio de KPIs y métricas de rendimiento.
Calcula y proporciona métricas del negocio.
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_, case
from app.extensions import db
from app.data.models import Order, Customer, Payment


class KPIService:
    """Servicio para cálculo de KPIs y métricas."""
    
    @staticmethod
    def get_dashboard_metrics(business_id):
        """
        Obtiene las métricas principales del dashboard.
        
        Args:
            business_id: ID del negocio
            
        Returns:
            dict: Diccionario con métricas
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Pedidos del día
        orders_today = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start
            )
        ).count()
        
        # Tiempo promedio de respuesta (en minutos)
        avg_response_seconds = db.session.query(
            func.avg(Order.response_time_seconds)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start,
                Order.response_time_seconds.isnot(None)
            )
        ).scalar()
        
        avg_response_minutes = round(avg_response_seconds / 60, 1) if avg_response_seconds else 0
        
        # Ventas del día
        sales_today = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start,
                Order.status.notin_(['cancelled'])
            )
        ).scalar()
        
        # Satisfacción (calculada en base a pedidos completados vs cancelados)
        completed_today = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start,
                Order.status.in_(['closed', 'paid'])
            )
        ).count()
        
        total_today = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= today_start
            )
        ).count()
        
        satisfaction = round((completed_today / total_today * 100), 1) if total_today > 0 else 0
        
        return {
            'orders_today': orders_today,
            'avg_response_time': avg_response_minutes,
            'sales_today': float(sales_today) if sales_today else 0,
            'satisfaction': satisfaction
        }
    
    @staticmethod
    def get_kpi_comparisons(business_id, period_days=30):
        """
        Obtiene comparaciones de KPIs con períodos anteriores.
        
        Args:
            business_id: ID del negocio
            period_days: Días del período a comparar
            
        Returns:
            dict: Diccionario con métricas y comparaciones
        """
        now = datetime.utcnow()
        current_period_start = now - timedelta(days=period_days)
        previous_period_start = current_period_start - timedelta(days=period_days)
        
        # Tiempo promedio de respuesta
        current_response_time = KPIService._get_avg_response_time(
            business_id, current_period_start, now
        )
        previous_response_time = KPIService._get_avg_response_time(
            business_id, previous_period_start, current_period_start
        )
        
        # Pedidos procesados
        current_orders = KPIService._get_orders_count(
            business_id, current_period_start, now
        )
        previous_orders = KPIService._get_orders_count(
            business_id, previous_period_start, current_period_start
        )
        
        # Tasa de conversión
        current_conversion = KPIService._get_conversion_rate(
            business_id, current_period_start, now
        )
        previous_conversion = KPIService._get_conversion_rate(
            business_id, previous_period_start, current_period_start
        )
        
        # Satisfacción del cliente (basada en pedidos completados)
        current_satisfaction = KPIService._get_satisfaction_score(
            business_id, current_period_start, now
        )
        previous_satisfaction = KPIService._get_satisfaction_score(
            business_id, previous_period_start, current_period_start
        )
        
        # Calcular porcentajes de cambio
        response_time_change = KPIService._calculate_percentage_change(
            previous_response_time, current_response_time, inverse=True
        )
        orders_change = KPIService._calculate_percentage_change(
            previous_orders, current_orders
        )
        conversion_change = KPIService._calculate_percentage_change(
            previous_conversion, current_conversion
        )
        satisfaction_change = KPIService._calculate_percentage_change(
            previous_satisfaction, current_satisfaction
        )
        
        return {
            'response_time': {
                'current': current_response_time,
                'previous': previous_response_time,
                'change': response_time_change,
                'improved': response_time_change > 0
            },
            'orders_processed': {
                'current': current_orders,
                'previous': previous_orders,
                'change': orders_change,
                'improved': orders_change > 0
            },
            'conversion_rate': {
                'current': current_conversion,
                'previous': previous_conversion,
                'change': conversion_change,
                'improved': conversion_change > 0
            },
            'satisfaction': {
                'current': current_satisfaction,
                'previous': previous_satisfaction,
                'change': satisfaction_change,
                'improved': satisfaction_change > 0
            }
        }
    
    @staticmethod
    def get_operational_metrics(business_id, period_days=30):
        """
        Obtiene métricas operativas detalladas.
        
        Args:
            business_id: ID del negocio
            period_days: Días del período
            
        Returns:
            dict: Métricas operativas
        """
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        # Tasa de automatización (pedidos con IA vs manuales)
        total_orders = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= period_start
            )
        ).count()
        
        # Asumiendo que todos los pedidos con response_time < 60 segundos son automatizados
        automated_orders = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= period_start,
                Order.response_time_seconds < 60
            )
        ).count()
        
        automation_rate = round((automated_orders / total_orders * 100), 1) if total_orders > 0 else 0
        
        # Tiempo ahorrado por semana (estimado)
        avg_manual_time = 5 * 60  # 5 minutos por pedido manual
        avg_auto_time = 30  # 30 segundos por pedido automatizado
        time_saved_per_order = (avg_manual_time - avg_auto_time) / 60  # en minutos
        
        weekly_orders = (total_orders / period_days) * 7
        time_saved_weekly = round((weekly_orders * time_saved_per_order) / 60, 1)  # en horas
        
        # Precisión de IA (pedidos sin errores)
        successful_orders = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= period_start,
                Order.status.in_(['closed', 'paid'])
            )
        ).count()
        
        ai_accuracy = round((successful_orders / total_orders * 100), 1) if total_orders > 0 else 0
        
        # Tasa de errores
        cancelled_orders = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= period_start,
                Order.status == 'cancelled'
            )
        ).count()
        
        error_rate = round((cancelled_orders / total_orders * 100), 1) if total_orders > 0 else 0
        
        return {
            'automation_rate': automation_rate,
            'time_saved_weekly_hours': time_saved_weekly,
            'ai_accuracy': ai_accuracy,
            'error_rate': error_rate
        }
    
    @staticmethod
    def get_financial_impact(business_id, period_days=30):
        """
        Calcula el impacto financiero.
        
        Args:
            business_id: ID del negocio
            period_days: Días del período
            
        Returns:
            dict: Métricas financieras
        """
        now = datetime.utcnow()
        current_period_start = now - timedelta(days=period_days)
        previous_period_start = current_period_start - timedelta(days=period_days)
        
        # Ventas actuales
        current_sales = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= current_period_start,
                Order.status.notin_(['cancelled'])
            )
        ).scalar()
        
        # Ventas anteriores
        previous_sales = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= previous_period_start,
                Order.created_at < current_period_start,
                Order.status.notin_(['cancelled'])
            )
        ).scalar()
        
        current_sales = float(current_sales) if current_sales else 0
        previous_sales = float(previous_sales) if previous_sales else 0
        
        # Incremento en ventas
        sales_increase = current_sales - previous_sales
        sales_increase_percentage = KPIService._calculate_percentage_change(
            previous_sales, current_sales
        )
        
        # Ahorro operativo estimado (basado en automatización)
        # Estimamos $5000 COP por hora de trabajo manual ahorrado
        time_saved_hours = KPIService.get_operational_metrics(business_id, period_days)['time_saved_weekly_hours']
        weekly_savings = time_saved_hours * 5000 * 4  # 4 semanas
        
        # ROI estimado (retorno de inversión)
        # Asumiendo un costo mensual de $90,000 COP (plan Pro)
        monthly_cost = 90000
        monthly_benefit = sales_increase + weekly_savings
        roi = round(((monthly_benefit - monthly_cost) / monthly_cost * 100), 1) if monthly_cost > 0 else 0
        
        return {
            'sales_increase': sales_increase,
            'sales_increase_percentage': sales_increase_percentage,
            'operational_savings': weekly_savings,
            'roi': roi,
            'total_sales_current': current_sales,
            'total_sales_previous': previous_sales
        }
    
    @staticmethod
    def get_orders_by_hour(business_id, days=7):
        """
        Obtiene la distribución de pedidos por hora del día.
        
        Args:
            business_id: ID del negocio
            days: Días a analizar
            
        Returns:
            dict: Pedidos por hora
        """
        period_start = datetime.utcnow() - timedelta(days=days)
        
        orders = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= period_start
            )
        ).all()
        
        hourly_distribution = {hour: 0 for hour in range(24)}
        
        for order in orders:
            hour = order.created_at.hour
            hourly_distribution[hour] += 1
        
        return hourly_distribution
    
    # Métodos auxiliares privados
    
    @staticmethod
    def _get_avg_response_time(business_id, start_date, end_date):
        """Calcula tiempo promedio de respuesta en minutos."""
        avg_seconds = db.session.query(
            func.avg(Order.response_time_seconds)
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date,
                Order.response_time_seconds.isnot(None)
            )
        ).scalar()
        
        return round(avg_seconds / 60, 1) if avg_seconds else 0
    
    @staticmethod
    def _get_orders_count(business_id, start_date, end_date):
        """Cuenta pedidos en un período."""
        return Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        ).count()
    
    @staticmethod
    def _get_conversion_rate(business_id, start_date, end_date):
        """Calcula tasa de conversión."""
        total = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        ).count()
        
        completed = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date,
                Order.status.in_(['closed', 'paid'])
            )
        ).count()
        
        return round((completed / total * 100), 1) if total > 0 else 0
    
    @staticmethod
    def _get_satisfaction_score(business_id, start_date, end_date):
        """Calcula score de satisfacción (1-5)."""
        total = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        ).count()
        
        completed = Order.query.filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at < end_date,
                Order.status.in_(['closed', 'paid'])
            )
        ).count()
        
        # Calculamos satisfacción en escala de 1 a 5
        conversion_rate = (completed / total) if total > 0 else 0
        satisfaction = round(1 + (conversion_rate * 4), 1)  # Escala 1-5
        
        return satisfaction
    
    @staticmethod
    def _calculate_percentage_change(old_value, new_value, inverse=False):
        """Calcula el porcentaje de cambio."""
        if old_value == 0:
            return 100 if new_value > 0 else 0
        
        change = ((new_value - old_value) / old_value) * 100
        
        # Para métricas donde menor es mejor (como tiempo de respuesta)
        if inverse:
            change = -change
        
        return round(change, 1)
