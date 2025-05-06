from extensions import db
from datetime import datetime

class Alerta(db.Model):
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