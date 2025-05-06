from extensions import db

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricula = db.Column(db.String(20))
    bastidor = db.Column(db.String(50), unique=True)
    referencia = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='activo')
    
    # La relación con tag está definida en el modelo Tag
    # tag = db.relationship('Tag', backref='vehiculo', uselist=False, lazy=True)
    
    def __init__(self, matricula=None, bastidor=None, referencia=None, estado='activo'):
        self.matricula = matricula
        self.bastidor = bastidor
        self.referencia = referencia
        self.estado = estado
    
    def to_dict(self):
        return {
            'id': self.id,
            'matricula': self.matricula,
            'bastidor': self.bastidor,
            'referencia': self.referencia,
            'estado': self.estado,
            'tag_id': self.tag.id if hasattr(self, 'tag') and self.tag else None
        }
    
    def __repr__(self):
        return f'<Vehiculo {self.id}: {self.matricula or self.bastidor}>'