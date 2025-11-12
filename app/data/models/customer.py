"""
Modelo de Cliente.
"""
from datetime import datetime, timezone
from app.extensions import db


class Customer(db.Model):
    """Modelo de cliente que hace pedidos."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    total_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relaciones
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'total_orders': self.total_orders
        }
    
    def __repr__(self):
        return f'<Customer {self.phone}>'
