from extensions import db

class Zona(db.Model):
    """
    Modelo Zona para representar áreas específicas dentro de los talleres
    ---
    properties:
      id:
        type: integer
        description: Identificador único de la zona
      nombre:
        type: string
        description: Nombre descriptivo de la zona
      tipo:
        type: string
        description: Clasificación de la zona (recepción, taller, pintura, etc.)
      color_hex:
        type: string
        description: Código de color hexadecimal para representar la zona en el plano
      taller_id:
        type: integer
        description: ID del taller al que pertenece esta zona
    """
    __tablename__ = 'zonas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20))
    color_hex = db.Column(db.String(7))
    taller_id = db.Column(db.Integer, db.ForeignKey('talleres.id'))
    
    # Relación
    taller = db.relationship('Taller', backref=db.backref('zonas', lazy=True))
    
    def __init__(self, nombre=None, tipo=None, color_hex=None, taller_id=None):
        self.nombre = nombre
        self.tipo = tipo
        self.color_hex = color_hex
        self.taller_id = taller_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'color_hex': self.color_hex,
            'taller_id': self.taller_id
        }
    
    def __repr__(self):
        return f'<Zona {self.id}: {self.nombre}>'