"""
Modelo de Pedido.
"""
from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    """Modelo de pedido."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Estados del Kanban
    status = db.Column(db.String(20), nullable=False, default='received')
    # Estados: received, preparing, ready, sent, paid, closed, cancelled
    
    # Tipo de pedido
    order_type = db.Column(db.String(20), default='delivery')  # delivery, pickup
    
    # Detalles del pedido
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Tiempos
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    accepted_at = db.Column(db.DateTime)  # Cuando se acepta el pedido
    preparing_at = db.Column(db.DateTime)  # Cuando se inicia preparación
    ready_at = db.Column(db.DateTime)  # Cuando está listo
    sent_at = db.Column(db.DateTime)  # Cuando se envía
    paid_at = db.Column(db.DateTime)  # Cuando se marca como pagado/entregado
    delivered_at = db.Column(db.DateTime)  # Cuando se entrega físicamente
    
    # Métricas
    response_time_seconds = db.Column(db.Integer)  # Tiempo de primera respuesta
    preparation_time_seconds = db.Column(db.Integer)  # Tiempo de preparación
    
    # Relaciones
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'business_id': self.business_id,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'status': self.status,
            'order_type': self.order_type,
            'total_amount': float(self.total_amount),
            'delivery_address': self.delivery_address,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'preparing_at': self.preparing_at.isoformat() if self.preparing_at else None,
            'ready_at': self.ready_at.isoformat() if self.ready_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'response_time_seconds': self.response_time_seconds,
            'preparation_time_seconds': self.preparation_time_seconds,
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
