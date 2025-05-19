from extensions import db
from datetime import datetime

class Posicion(db.Model):
    """
    Modelo Posicion para registrar las ubicaciones de los tags UWB dentro del taller
    ---
    properties:
    id:
        type: integer
        description: Identificador único del registro de posición
    tag_id:
        type: integer
        description: ID del tag UWB cuya posición se está registrando
    x:
        type: integer
        description: Coordenada X en el plano del taller (en centímetros)
    y:
        type: integer
        description: Coordenada Y en el plano del taller (en centímetros)
    zona_id:
        type: integer
        description: ID de la zona donde se encuentra el tag
    timestamp:
        type: string
        format: date-time
        description: Fecha y hora en que se registró la posición
    """
    __tablename__ = 'posiciones'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    zona_id = db.Column(db.Integer, db.ForeignKey('zonas.id'))
    timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relaciones
    tag = db.relationship('Tag', backref=db.backref('posiciones', lazy=True))
    zona = db.relationship('Zona', backref=db.backref('posiciones', lazy=True))
    
    def __init__(self, tag_id=None, x=0, y=0, zona_id=None):
        self.tag_id = tag_id
        self.x = x
        self.y = y
        self.zona_id = zona_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'x': self.x,
            'y': self.y,
            'zona_id': self.zona_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Posicion {self.id}: Tag {self.tag_id} en ({self.x},{self.y})>'