"""
Modelo de Mensaje de WhatsApp.
"""
from datetime import datetime, timezone
from app.extensions import db


class Message(db.Model):
    """Modelo de mensaje de WhatsApp."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    whatsapp_message_id = db.Column(db.String(100), unique=True)
    sender_phone = db.Column(db.String(20), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, document, location
    content = db.Column(db.Text)
    media_url = db.Column(db.String(255))
    direction = db.Column(db.String(10), nullable=False)  # inbound, outbound
    is_automated = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'whatsapp_message_id': self.whatsapp_message_id,
            'sender_phone': self.sender_phone,
            'receiver_phone': self.receiver_phone,
            'message_type': self.message_type,
            'content': self.content,
            'media_url': self.media_url,
            'direction': self.direction,
            'is_automated': self.is_automated,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id} - {self.direction}>'
