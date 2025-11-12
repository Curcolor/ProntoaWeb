"""
Schemas para el modelo Customer.
"""
from app.extensions import ma
from app.data.models.customer import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Customer.
    
    Propósito:
    - Convierte objetos Customer a JSON
    - Útil para mostrar información de clientes en pedidos
    
    Uso:
        customer = Customer.query.filter_by(phone='+573001234567').first()
        customer_schema = CustomerSchema()
        json_data = customer_schema.dump(customer)
    """
    
    class Meta:
        model = Customer
        load_instance = True


# Instancias para uso directo
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
