"""
Schemas para los modelos Order y OrderItem.
"""
from marshmallow import fields
from app.extensions import ma
from app.data.models.order import Order
from app.data.models.order_item import OrderItem


class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo OrderItem.
    
    Propósito:
    - Convierte ítems de pedido a JSON
    - Incluye información del producto relacionado
    
    Uso:
        item = OrderItem.query.get(1)
        item_schema = OrderItemSchema()
        json_data = item_schema.dump(item)
    """
    
    class Meta:
        model = OrderItem
        load_instance = True
        include_fk = True
    
    # Importación lazy para evitar circular imports
    product = fields.Nested('ProductSchema', dump_only=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Order.
    
    Propósito:
    - Convierte pedidos completos a JSON
    - Incluye items, customer y business anidados
    - Usado en API REST para enviar pedidos al frontend
    
    Uso:
        order = Order.query.get(1)
        order_schema = OrderSchema()
        json_data = order_schema.dump(order)
        # {
        #   "id": 1,
        #   "order_number": "1202511100001",
        #   "customer": {...},
        #   "items": [...],
        #   "total_amount": 50000
        # }
    """
    
    class Meta:
        model = Order
        load_instance = True
        include_fk = True
    
    customer = fields.Nested('CustomerSchema', dump_only=True)
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    business = fields.Nested('BusinessSchema', dump_only=True)


# Instancias para uso directo
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
