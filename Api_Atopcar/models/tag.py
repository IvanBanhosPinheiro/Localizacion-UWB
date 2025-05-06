from extensions import db
from datetime import datetime

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    mac = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    bateria = db.Column(db.Integer)
    ultima_comunicacion = db.Column(db.TIMESTAMP)
    observaciones = db.Column(db.Text)
    
    # Relación con vehículo (uno a uno)
    vehiculo = db.relationship('Vehiculo', backref=db.backref('tag', uselist=False), lazy=True)
    
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