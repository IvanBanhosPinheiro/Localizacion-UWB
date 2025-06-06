from extensions import db

class Distancia(db.Model):
    """
    Modelo Distancia para almacenar mediciones de distancia entre tags móviles y anchors fijos
    ---
    properties:
    id:
        type: integer
        description: Identificador único del registro de distancia
    tag_id:
        type: integer
        description: ID del tag UWB móvil desde el que se realizan las mediciones
    anchor1_id:
        type: integer
        description: ID del primer anchor de referencia
    anchor1_dist:
        type: number
        format: float
        description: Distancia en metros entre el tag y el primer anchor
    anchor2_id:
        type: integer
        description: ID del segundo anchor de referencia
    anchor2_dist:
        type: number
        format: float
        description: Distancia en metros entre el tag y el segundo anchor
    anchor3_id:
        type: integer
        description: ID del tercer anchor de referencia
    anchor3_dist:
        type: number
        format: float
        description: Distancia en metros entre el tag y el tercer anchor
    """
    __tablename__ = 'distancias'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), unique=True)
    anchor1_id = db.Column(db.Integer, db.ForeignKey('anchors.id'))
    anchor1_dist = db.Column(db.Float)
    anchor2_id = db.Column(db.Integer, db.ForeignKey('anchors.id'))
    anchor2_dist = db.Column(db.Float)
    anchor3_id = db.Column(db.Integer, db.ForeignKey('anchors.id'))
    anchor3_dist = db.Column(db.Float)
    
    # Relaciones
    tag = db.relationship('Tag', backref=db.backref('distancia', uselist=False, lazy=True))
    anchor1 = db.relationship('Anchor', foreign_keys=[anchor1_id])
    anchor2 = db.relationship('Anchor', foreign_keys=[anchor2_id])
    anchor3 = db.relationship('Anchor', foreign_keys=[anchor3_id])
    
    def __init__(self, tag_id=None, anchor1_id=None, anchor1_dist=None,
                 anchor2_id=None, anchor2_dist=None, anchor3_id=None, anchor3_dist=None):
        self.tag_id = tag_id
        self.anchor1_id = anchor1_id
        self.anchor1_dist = anchor1_dist
        self.anchor2_id = anchor2_id
        self.anchor2_dist = anchor2_dist
        self.anchor3_id = anchor3_id
        self.anchor3_dist = anchor3_dist
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'anchor1_id': self.anchor1_id,
            'anchor1_dist': self.anchor1_dist,
            'anchor2_id': self.anchor2_id,
            'anchor2_dist': self.anchor2_dist,
            'anchor3_id': self.anchor3_id,
            'anchor3_dist': self.anchor3_dist
        }
    
    def __repr__(self):
        return f'<Distancia {self.id}: Tag {self.tag_id}>'