from extensions import db
from datetime import datetime

class Taller(db.Model):
    """
    Modelo Taller para representar los espacios físicos donde se realiza el seguimiento UWB
    ---
    properties:
    id:
        type: integer
        description: Identificador único del taller
    nombre:
        type: string
        description: Nombre del taller o instalación
    svg_plano:
        type: string
        description: Representación SVG del plano del taller
    creado_en:
        type: string
        format: date-time
        description: Fecha y hora de registro del taller en el sistema
    """
    __tablename__ = 'talleres'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    svg_plano = db.Column(db.Text)
    creado_en = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relaciones implícitas
    # zonas = db.relationship('Zona', backref='taller', lazy=True)
    # anchors = db.relationship('Anchor', backref='taller', lazy=True)
    
    def __init__(self, nombre=None, svg_plano=None):
        self.nombre = nombre
        self.svg_plano = svg_plano
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'svg_plano': self.svg_plano,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
    
    def __repr__(self):
        return f'<Taller {self.id}: {self.nombre}>'