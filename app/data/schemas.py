"""
Schemas de Marshmallow para serialización y validación de datos.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.extensions import ma
from app.data.models import (
    User, Business, Customer, Product, Order, 
    OrderItem, Message, Notification, Payment
)


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo User."""
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
        
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))


class BusinessSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Business."""
    
    class Meta:
        model = Business
        load_instance = True
        include_fk = True


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Customer."""
    
    class Meta:
        model = Customer
        load_instance = True


class ProductSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Product."""
    
    class Meta:
        model = Product
        load_instance = True
        include_fk = True


class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo OrderItem."""
    
    class Meta:
        model = OrderItem
        load_instance = True
        include_fk = True
    
    product = fields.Nested(ProductSchema, dump_only=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Order."""
    
    class Meta:
        model = Order
        load_instance = True
        include_fk = True
    
    customer = fields.Nested(CustomerSchema, dump_only=True)
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    business = fields.Nested(BusinessSchema, dump_only=True)


class MessageSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Message."""
    
    class Meta:
        model = Message
        load_instance = True
        include_fk = True


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Notification."""
    
    class Meta:
        model = Notification
        load_instance = True
        include_fk = True


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    """Schema para el modelo Payment."""
    
    class Meta:
        model = Payment
        load_instance = True
        include_fk = True


# Schemas para validación de entrada

class LoginSchema(Schema):
    """Schema para validar login."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
    remember = fields.Boolean(load_default=False)


class RegisterSchema(Schema):
    """Schema para validar registro."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True)
    full_name = fields.Str(required=True, validate=validate.Length(min=3))
    phone = fields.Str(required=True)
    business_name = fields.Str(required=True)
    business_type = fields.Str(required=True)
    
    @validates('confirm_password')
    def validate_password_match(self, value, **kwargs):
        """Valida que las contraseñas coincidan."""
        if 'password' in self.context and value != self.context['password']:
            raise ValidationError('Las contraseñas no coinciden')


class OrderCreateSchema(Schema):
    """Schema para crear un pedido."""
    customer_phone = fields.Str(required=True)
    customer_name = fields.Str(required=False)
    order_type = fields.Str(validate=validate.OneOf(['delivery', 'pickup']))
    delivery_address = fields.Str(required=False)
    notes = fields.Str(required=False)
    items = fields.List(fields.Dict(), required=True)


class OrderUpdateSchema(Schema):
    """Schema para actualizar un pedido."""
    status = fields.Str(validate=validate.OneOf([
        'received', 'preparing', 'ready', 'sent', 'paid', 'closed', 'cancelled'
    ]))
    notes = fields.Str()


class MessageSendSchema(Schema):
    """Schema para enviar un mensaje."""
    phone = fields.Str(required=True)
    content = fields.Str(required=True)
    message_type = fields.Str(validate=validate.OneOf(['text', 'image', 'document']))


# Instancias de schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

business_schema = BusinessSchema()
businesses_schema = BusinessSchema(many=True)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)

payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

login_schema = LoginSchema()
register_schema = RegisterSchema()
order_create_schema = OrderCreateSchema()
order_update_schema = OrderUpdateSchema()
message_send_schema = MessageSendSchema()
