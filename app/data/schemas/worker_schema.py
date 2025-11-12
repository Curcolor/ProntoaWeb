"""
Schemas para el modelo Worker.
"""
from marshmallow import fields, validate
from app.extensions import ma
from app.data.models.worker import Worker


class WorkerSchema(ma.SQLAlchemyAutoSchema):
    """
    Schema para serialización del modelo Worker.
    
    Propósito:
    - Convierte trabajadores a JSON
    - Excluye password por seguridad
    - Valida worker_type (planta o repartidor)
    
    Uso:
        worker = Worker.query.get(1)
        worker_schema = WorkerSchema()
        json_data = worker_schema.dump(worker)
    """
    
    class Meta:
        model = Worker
        load_instance = True
        include_fk = True
        exclude = ('password_hash',)  # ❌ Nunca exponer password
        
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))
    worker_type = fields.Str(validate=validate.OneOf(['planta', 'repartidor']))


# Instancias para uso directo
worker_schema = WorkerSchema()
workers_schema = WorkerSchema(many=True)
