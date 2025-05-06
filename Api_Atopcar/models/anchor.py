from extensions import db

class Anchor(db.Model):
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