"""
Schemas para el modelo Payment.
"""
from app.extensions import ma
from app.data.models.payment import Payment


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Payment.
    
    Propósito:
    - Convierte pagos a JSON
    - Valida métodos de pago y montos
    
    Uso:
        payment = Payment.query.filter_by(order_id=1).first()
        payment_schema = PaymentSchema()
        json_data = payment_schema.dump(payment)
    """
    
    class Meta:
        model = Payment
        load_instance = True
        include_fk = True


# Instancias para uso directo
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
