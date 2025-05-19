from extensions import db

class Usuario(db.Model):
    """
    Modelo Usuario para gestionar las cuentas de acceso al sistema
    ---
    properties:
      id:
        type: integer
        description: Identificador único del usuario
      username:
        type: string
        description: Nombre de usuario único para iniciar sesión
      nombre_completo:
        type: string
        description: Nombre y apellidos del usuario
      rol:
        type: string
        description: Nivel de acceso y permisos del usuario
        enum: [administrador, supervisor, técnico, recepcionista]
      activo:
        type: boolean
        description: Indica si la cuenta de usuario está habilitada
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    nombre_completo = db.Column(db.String(100))
    rol = db.Column(db.String(20), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    def __init__(self, username=None, password_hash=None, nombre_completo=None, 
                 rol='recepcionista', activo=True):
        self.username = username
        self.password_hash = password_hash
        self.nombre_completo = nombre_completo
        self.rol = rol
        self.activo = activo
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Usuario {self.id}: {self.username}>'