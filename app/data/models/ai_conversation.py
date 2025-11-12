"""
Modelo de Conversación de IA.
"""
from datetime import datetime, timezone
from app.extensions import db


class AIConversation(db.Model):
    """Modelo para almacenar conversaciones procesadas por IA."""
    __tablename__ = 'ai_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    conversation_context = db.Column(db.JSON)  # Contexto de la conversación
    extracted_intent = db.Column(db.String(50))  # order, inquiry, complaint, etc.
    extracted_entities = db.Column(db.JSON)  # Entidades extraídas (productos, cantidades, etc.)
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relación
    business = db.relationship('Business', backref='ai_conversations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_phone': self.customer_phone,
            'business_id': self.business_id,
            'conversation_context': self.conversation_context,
            'extracted_intent': self.extracted_intent,
            'extracted_entities': self.extracted_entities,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIConversation {self.id} - {self.extracted_intent}>'
