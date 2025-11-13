"""
Schemas para el modelo User.
"""
from marshmallow import fields, validate
from app.extensions import ma
from app.data.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo User.
    
    Propósito:
    - Convierte objetos User a JSON (serialización)
    - Convierte JSON a objetos User (deserialización)
    - Excluye el password_hash por seguridad
    
    Uso:
        user = User.query.get(1)
        user_schema = UserSchema()
        json_data = user_schema.dump(user)
    """
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)  # Nunca exponer password
        
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))


# Instancias para uso directo
user_schema = UserSchema()
users_schema = UserSchema(many=True)
