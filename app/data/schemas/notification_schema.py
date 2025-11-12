"""
Schemas para el modelo Notification.
"""
from app.extensions import ma
from app.data.models.notification import Notification


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Notification.
    
    Propósito:
    - Convierte notificaciones a JSON
    - Usado para mostrar alertas en el dashboard
    
    Uso:
        notifications = Notification.query.filter_by(user_id=1, is_read=False).all()
        notifications_schema = NotificationSchema(many=True)
        json_data = notifications_schema.dump(notifications)
    """
    
    class Meta:
        model = Notification
        load_instance = True
        include_fk = True


# Instancias para uso directo
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
