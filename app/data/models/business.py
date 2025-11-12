"""
Modelo de Negocio.
"""
from datetime import datetime, timezone
from app.extensions import db


class Business(db.Model):
    """Modelo de negocio."""
    __tablename__ = 'businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)  # restaurant, bakery, pharmacy, etc.
    address = db.Column(db.String(200))
    city = db.Column(db.String(50), default='Barranquilla')
    whatsapp_number = db.Column(db.String(20), unique=True)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    delivery_enabled = db.Column(db.Boolean, default=True)
    pickup_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    subscription_plan = db.Column(db.String(20), default='basic')  # basic, pro, enterprise
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    orders = db.relationship('Order', backref='business', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='business', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el negocio a diccionario."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'business_type': self.business_type,
            'address': self.address,
            'city': self.city,
            'whatsapp_number': self.whatsapp_number,
            'opening_time': self.opening_time.strftime('%H:%M') if self.opening_time else None,
            'closing_time': self.closing_time.strftime('%H:%M') if self.closing_time else None,
            'delivery_enabled': self.delivery_enabled,
            'pickup_enabled': self.pickup_enabled,
            'is_active': self.is_active,
            'subscription_plan': self.subscription_plan
        }
    
    def __repr__(self):
        return f'<Business {self.name}>'
