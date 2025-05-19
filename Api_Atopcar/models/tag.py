from extensions import db
from datetime import datetime

class Tag(db.Model):
    """
    Modelo Tag para dispositivos UWB móviles que se asocian a vehículos
    ---
    properties:
    id:
        type: integer
        description: Identificador único del tag
    codigo:
        type: string
        description: Código único de identificación del tag
    mac:
        type: string
        description: Dirección MAC única del dispositivo UWB
    estado:
        type: string
        description: Estado actual del tag
        enum: [libre, asignado, averiado, baja, mantenimiento]
    bateria:
        type: integer
        description: Nivel de batería del dispositivo (porcentaje)
    ultima_comunicacion:
        type: string
        format: date-time
        description: Fecha y hora de la última comunicación recibida
    observaciones:
        type: string
        description: Notas adicionales sobre el tag
    vehiculo_id:
        type: integer
        description: ID del vehículo al que está asociado (si aplica)
    """
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    mac = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    bateria = db.Column(db.Integer)
    ultima_comunicacion = db.Column(db.TIMESTAMP)
    observaciones = db.Column(db.Text)
    
    vehiculo = db.relationship('Vehiculo', back_populates='tag', uselist=False)
    
    def __init__(self, codigo=None, mac=None, estado='libre', 
                 bateria=None, ultima_comunicacion=None, observaciones=None):
        self.codigo = codigo
        self.mac = mac
        self.estado = estado
        self.bateria = bateria
        self.ultima_comunicacion = ultima_comunicacion or datetime.utcnow()
        self.observaciones = observaciones
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'mac': self.mac,
            'estado': self.estado,
            'bateria': self.bateria,
            'ultima_comunicacion': self.ultima_comunicacion.isoformat() if self.ultima_comunicacion else None,
            'observaciones': self.observaciones,
            'vehiculo_id': self.vehiculo.id if self.vehiculo else None
        }
    
    def __repr__(self):
        return f'<Tag {self.id}: {self.codigo}>'