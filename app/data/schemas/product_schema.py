"""
Schemas para el modelo Product.
"""
from app.extensions import ma
from app.data.models.product import Product


class ProductSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Product.
    
    Propósito:
    - Convierte productos a JSON para catálogo
    - Valida precios y cantidades
    
    Uso:
        product = Product.query.get(1)
        product_schema = ProductSchema()
        json_data = product_schema.dump(product)
        # {"id": 1, "name": "Pan", "price": 2500.0, ...}
    """
    
    class Meta:
        model = Product
        load_instance = True
        include_fk = True


# Instancias para uso directo
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
