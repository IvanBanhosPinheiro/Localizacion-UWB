from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario
import bcrypt

# Crear el blueprint para los usuarios
usuario_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

# Obtener todos los usuarios
@usuario_bp.route('/', methods=['GET'])
def get_all_usuarios():
    # Filtrar por rol si se especifica
    rol = request.args.get('rol')
    # Filtrar por activo/inactivo
    activo = request.args.get('activo')
    
    query = Usuario.query
    
    if rol:
        query = query.filter_by(rol=rol)
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        query = query.filter_by(activo=activo_bool)
    
    usuarios = query.all()
    return jsonify([usuario.to_dict() for usuario in usuarios])

# Obtener un usuario específico
@usuario_bp.route('/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_dict())

# Crear un nuevo usuario
@usuario_bp.route('/', methods=['POST'])
def create_usuario():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "El nombre de usuario y la contraseña son obligatorios"}), 400
    
    # Verificar que el nombre de usuario sea único
    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({"error": f"El nombre de usuario '{data['username']}' ya está en uso"}), 400
    
    # Hashear la contraseña
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    nuevo_usuario = Usuario(
        username=data['username'],
        password_hash=password_hash,
        nombre_completo=data.get('nombre_completo'),
        rol=data.get('rol', 'recepcionista'),
        activo=data.get('activo', True)
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify(nuevo_usuario.to_dict()), 201

# Actualizar un usuario
@usuario_bp.route('/<int:id>', methods=['PUT'])
def update_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.json
    
    # Verificar que el nombre de usuario sea único si se cambia
    if 'username' in data and data['username'] != usuario.username:
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({"error": f"El nombre de usuario '{data['username']}' ya está en uso"}), 400
    
    # Actualizar campos
    if 'username' in data:
        usuario.username = data['username']
    if 'password' in data:
        usuario.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if 'nombre_completo' in data:
        usuario.nombre_completo = data['nombre_completo']
    if 'rol' in data:
        usuario.rol = data['rol']
    if 'activo' in data:
        usuario.activo = data['activo']
    
    db.session.commit()
    
    return jsonify(usuario.to_dict())

# Eliminar un usuario
@usuario_bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    
    return '', 204

# Cambiar contraseña
@usuario_bp.route('/<int:id>/cambiar-password', methods=['PUT'])
def cambiar_password(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.json
    
    if not data.get('password_actual') or not data.get('password_nueva'):
        return jsonify({"error": "La contraseña actual y la nueva son obligatorias"}), 400
    
    # Verificar contraseña actual
    if not bcrypt.checkpw(data['password_actual'].encode('utf-8'), usuario.password_hash.encode('utf-8')):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 401
    
    # Hashear nueva contraseña
    usuario.password_hash = bcrypt.hashpw(data['password_nueva'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    
    return jsonify({"mensaje": "Contraseña cambiada correctamente"})

# Activar/desactivar un usuario
@usuario_bp.route('/<int:id>/toggle-activo', methods=['PUT'])
def toggle_activo(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    return jsonify(usuario.to_dict())