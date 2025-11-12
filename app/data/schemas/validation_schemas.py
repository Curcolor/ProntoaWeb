"""
Schemas de validación para requests de API.
Estos schemas NO están asociados a modelos, solo validan datos de entrada.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class LoginSchema(Schema):
    """
    Schema para validar requests de login.
    
    Propósito:
    - Valida que email y password estén presentes
    - Valida formato de email
    
    Uso en API:
        @app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            errors = login_schema.validate(data)
            if errors:
                return jsonify({'errors': errors}), 400
    """
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
    remember = fields.Boolean(load_default=False)


class RegisterSchema(Schema):
    """
    Schema para validar requests de registro.
    
    Propósito:
    - Valida todos los campos requeridos
    - Verifica que las contraseñas coincidan
    - Valida longitud mínima de password
    
    Uso en API:
        @app.route('/api/auth/register', methods=['POST'])
        def register():
            data = request.get_json()
            errors = register_schema.validate(data)
            if errors:
                return jsonify({'errors': errors}), 400
    """
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
    """
    Schema para validar requests de creación de pedidos.
    
    Propósito:
    - Valida datos mínimos para crear un pedido
    - Verifica que items sea una lista
    
    Uso en API:
        @app.route('/api/orders', methods=['POST'])
        def create_order():
            data = request.get_json()
            errors = order_create_schema.validate(data)
            if errors:
                return jsonify({'errors': errors}), 400
    """
    customer_phone = fields.Str(required=True)
    customer_name = fields.Str(required=False)
    order_type = fields.Str(validate=validate.OneOf(['delivery', 'pickup']))
    delivery_address = fields.Str(required=False)
    notes = fields.Str(required=False)
    items = fields.List(fields.Dict(), required=True)


class OrderUpdateSchema(Schema):
    """
    Schema para validar requests de actualización de pedidos.
    
    Propósito:
    - Valida que el status sea uno de los permitidos
    - Permite actualizar notas
    
    Uso en API:
        @app.route('/api/orders/<int:id>', methods=['PATCH'])
        def update_order(id):
            data = request.get_json()
            errors = order_update_schema.validate(data)
            if errors:
                return jsonify({'errors': errors}), 400
    """
    status = fields.Str(validate=validate.OneOf([
        'received', 'preparing', 'ready', 'sent', 'paid', 'closed', 'cancelled'
    ]))
    notes = fields.Str()


class MessageSendSchema(Schema):
    """
    Schema para validar requests de envío de mensajes.
    
    Propósito:
    - Valida datos para enviar mensajes por WhatsApp
    - Verifica tipo de mensaje
    
    Uso en API:
        @app.route('/api/whatsapp/send', methods=['POST'])
        def send_message():
            data = request.get_json()
            errors = message_send_schema.validate(data)
            if errors:
                return jsonify({'errors': errors}), 400
    """
    phone = fields.Str(required=True)
    content = fields.Str(required=True)
    message_type = fields.Str(validate=validate.OneOf(['text', 'image', 'document']))


# Instancias para uso directo
login_schema = LoginSchema()
register_schema = RegisterSchema()
order_create_schema = OrderCreateSchema()
order_update_schema = OrderUpdateSchema()
message_send_schema = MessageSendSchema()
