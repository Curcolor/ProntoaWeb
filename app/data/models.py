"""
Modelos de base de datos para ProntoaWeb.
Define todas las entidades y sus relaciones.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    """Modelo de usuario del sistema."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    business = db.relationship('Business', backref='owner', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Establece el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte el usuario a diccionario."""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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


class Customer(db.Model):
    """Modelo de cliente que hace pedidos."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    total_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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


class Product(db.Model):
    """Modelo de producto del catálogo."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_id': self.business_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category,
            'is_available': self.is_available,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
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
            'ready_at': self.ready_at.isoformat() if self.ready_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'response_time_seconds': self.response_time_seconds,
            'preparation_time_seconds': self.preparation_time_seconds,
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Modelo de ítem de pedido."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    # Relación con producto
    product = db.relationship('Product', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal),
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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


class Notification(db.Model):
    """Modelo de notificación del sistema."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    related_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = db.relationship('User', backref='notifications')
    related_order = db.relationship('Order', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'related_order_id': self.related_order_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'


class Payment(db.Model):
    """Modelo de pago."""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, transfer, stripe
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    transaction_id = db.Column(db.String(100), unique=True)
    stripe_payment_intent_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.payment_status}>'


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
