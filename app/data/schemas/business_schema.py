"""
Schemas para el modelo Business.
"""
from app.extensions import ma
from app.data.models.business import Business


class BusinessSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Business.
    
    Propósito:
    - Convierte objetos Business a JSON
    - Valida datos de entrada al crear/actualizar negocios
    
    Uso:
        business = Business.query.get(1)
        business_schema = BusinessSchema()
        json_data = business_schema.dump(business)
    """
    
    class Meta:
        model = Business
        load_instance = True
        include_fk = True


# Instancias para uso directo
business_schema = BusinessSchema()
businesses_schema = BusinessSchema(many=True)
