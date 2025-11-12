"""
Schemas para el modelo Message.
"""
from app.extensions import ma
from app.data.models.message import Message


class MessageSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Message.
    
    Propósito:
    - Convierte mensajes de WhatsApp a JSON
    - Útil para mostrar historial de conversaciones
    
    Uso:
        message = Message.query.filter_by(order_id=1).all()
        messages_schema = MessageSchema(many=True)
        json_data = messages_schema.dump(message)
    """
    
    class Meta:
        model = Message
        load_instance = True
        include_fk = True


# Instancias para uso directo
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
