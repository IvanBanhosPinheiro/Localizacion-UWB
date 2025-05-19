from extensions import db
from datetime import datetime

class Alerta(db.Model):
    """
    Modelo Alerta para la gestión de notificaciones del sistema
    ---
    properties:
      id:
        type: integer
        description: Identificador único de la alerta
      tag_id:
        type: integer
        description: ID del tag UWB asociado a esta alerta
      vehiculo_id:
        type: integer
        description: ID del vehículo asociado a esta alerta
      tipo:
        type: string
        description: Categoría de la alerta (batería baja, fuera de zona, etc.)
        enum: [bateria_baja, fuera_de_zona, movimiento_no_autorizado, averia, otros]
      descripcion:
        type: string
        description: Detalles adicionales sobre la alerta
      timestamp:
        type: string
        format: date-time
        description: Fecha y hora cuando se generó la alerta
      leido:
        type: boolean
        description: Indica si la alerta ha sido revisada por un usuario
    """
    __tablename__ = 'alertas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    tipo = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.Text)
    timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    
    # Relaciones
    tag = db.relationship('Tag', backref=db.backref('alertas', lazy=True))
    vehiculo = db.relationship('Vehiculo', backref=db.backref('alertas', lazy=True))
    
    def __init__(self, tag_id=None, vehiculo_id=None, tipo='otros', descripcion=None, leido=False):
        self.tag_id = tag_id
        self.vehiculo_id = vehiculo_id
        self.tipo = tipo
        self.descripcion = descripcion
        self.leido = leido
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'vehiculo_id': self.vehiculo_id,
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'leido': self.leido
        }
    
    def __repr__(self):
        return f'<Alerta {self.id}: {self.tipo}>'