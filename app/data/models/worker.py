"""
Modelo de Trabajador.
"""
from datetime import datetime, timezone, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Worker(UserMixin, db.Model):
    """Modelo de trabajador del negocio (2 tipos: planta y repartidor)."""
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    
    # Tipo de trabajador: 'planta' (cocina/preparación) o 'repartidor' (delivery)
    worker_type = db.Column(db.String(20), nullable=False, default='planta')
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relación
    business = db.relationship('Business', backref='workers')
    
    def set_password(self, password):
        """Establece el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte el trabajador a diccionario."""
        return {
            'id': self.id,
            'business_id': self.business_id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'worker_type': self.worker_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Worker {self.email}>'
