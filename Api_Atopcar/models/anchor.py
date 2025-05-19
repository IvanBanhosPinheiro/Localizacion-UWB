from extensions import db

class Anchor(db.Model):
    """
    Modelo Anchor para dispositivos UWB fijos que sirven como puntos de referencia
    ---
    properties:
      id:
        type: integer
        description: Identificador único del anchor
      nombre:
        type: string
        description: Nombre descriptivo del anchor
      mac:
        type: string
        description: Dirección MAC única del dispositivo UWB
      x:
        type: integer
        description: Coordenada X de la posición del anchor en el plano del taller
      y:
        type: integer
        description: Coordenada Y de la posición del anchor en el plano del taller
      canal_rf:
        type: string
        description: Canal de radiofrecuencia en el que opera el dispositivo
      zona_id:
        type: integer
        description: ID de la zona donde está instalado el anchor
      taller_id:
        type: integer
        description: ID del taller donde está instalado el anchor
      activo:
        type: boolean
        description: Indica si el anchor está operativo actualmente
    """
    __tablename__ = 'anchors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    mac = db.Column(db.String(50), unique=True, nullable=False)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    canal_rf = db.Column(db.String(10))
    zona_id = db.Column(db.Integer, db.ForeignKey('zonas.id'))
    taller_id = db.Column(db.Integer, db.ForeignKey('talleres.id'))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    zona = db.relationship('Zona', backref=db.backref('anchors', lazy=True))
    taller = db.relationship('Taller', backref=db.backref('anchors', lazy=True))
    
    def __init__(self, nombre=None, mac=None, x=None, y=None, canal_rf=None, 
                 zona_id=None, taller_id=None, activo=True):
        self.nombre = nombre
        self.mac = mac
        self.x = x
        self.y = y
        self.canal_rf = canal_rf
        self.zona_id = zona_id
        self.taller_id = taller_id
        self.activo = activo
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'mac': self.mac,
            'x': self.x,
            'y': self.y,
            'canal_rf': self.canal_rf,
            'zona_id': self.zona_id,
            'taller_id': self.taller_id,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Anchor {self.id}: {self.nombre or self.mac}>'