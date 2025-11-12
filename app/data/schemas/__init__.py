"""
Schemas de Marshmallow
"""
# Model Schemas
from app.data.schemas.user_schema import UserSchema, user_schema, users_schema
from app.data.schemas.business_schema import BusinessSchema, business_schema, businesses_schema
from app.data.schemas.customer_schema import CustomerSchema, customer_schema, customers_schema
from app.data.schemas.product_schema import ProductSchema, product_schema, products_schema
from app.data.schemas.order_schema import (
    OrderSchema, OrderItemSchema,
    order_schema, orders_schema,
    order_item_schema, order_items_schema
)
from app.data.schemas.message_schema import MessageSchema, message_schema, messages_schema
from app.data.schemas.notification_schema import NotificationSchema, notification_schema, notifications_schema
from app.data.schemas.payment_schema import PaymentSchema, payment_schema, payments_schema
from app.data.schemas.worker_schema import WorkerSchema, worker_schema, workers_schema

# Validation Schemas
from app.data.schemas.validation_schemas import (
    LoginSchema, RegisterSchema,
    OrderCreateSchema, OrderUpdateSchema,
    MessageSendSchema,
    login_schema, register_schema,
    order_create_schema, order_update_schema,
    message_send_schema
)

__all__ = [
    # Model Schema Classes
    'UserSchema',
    'BusinessSchema',
    'CustomerSchema',
    'ProductSchema',
    'OrderSchema',
    'OrderItemSchema',
    'MessageSchema',
    'NotificationSchema',
    'PaymentSchema',
    'WorkerSchema',
    
    # Model Schema Instances
    'user_schema',
    'users_schema',
    'business_schema',
    'businesses_schema',
    'customer_schema',
    'customers_schema',
    'product_schema',
    'products_schema',
    'order_schema',
    'orders_schema',
    'order_item_schema',
    'order_items_schema',
    'message_schema',
    'messages_schema',
    'notification_schema',
    'notifications_schema',
    'payment_schema',
    'payments_schema',
    'worker_schema',
    'workers_schema',
    
    # Validation Schema Classes
    'LoginSchema',
    'RegisterSchema',
    'OrderCreateSchema',
    'OrderUpdateSchema',
    'MessageSendSchema',
    
    # Validation Schema Instances
    'login_schema',
    'register_schema',
    'order_create_schema',
    'order_update_schema',
    'message_send_schema',
]
