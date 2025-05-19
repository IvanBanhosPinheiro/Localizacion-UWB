from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario
import bcrypt
from flasgger import swag_from

# Crear el blueprint para los usuarios
usuario_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

# Obtener todos los usuarios
@usuario_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Obtener todos los usuarios',
    'description': 'Recupera la lista completa de usuarios con opciones de filtrado',
    'parameters': [
        {
            'name': 'rol',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrar por rol (administrador, supervisor, técnico, recepcionista)'
        },
        {
            'name': 'activo',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar usuarios activos o inactivos (true/false)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de usuarios',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Usuario'}
            }
        }
    }
})
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
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Obtener un usuario específico',
    'description': 'Recupera los detalles de un usuario por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles del usuario',
            'schema': {'$ref': '#/definitions/Usuario'}
        },
        404: {
            'description': 'Usuario no encontrado'
        }
    }
})
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_dict())

# Crear un nuevo usuario
@usuario_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Crear un nuevo usuario',
    'description': 'Registra un nuevo usuario en el sistema',
    'parameters': [
        {
            'name': 'usuario',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Nombre de usuario único'},
                    'password': {'type': 'string', 'description': 'Contraseña del usuario'},
                    'nombre_completo': {'type': 'string', 'description': 'Nombre y apellidos del usuario'},
                    'rol': {'type': 'string', 'description': 'Rol del usuario', 'enum': ['administrador', 'supervisor', 'técnico', 'recepcionista']},
                    'activo': {'type': 'boolean', 'description': 'Estado de la cuenta', 'default': True}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Usuario creado exitosamente',
            'schema': {'$ref': '#/definitions/Usuario'}
        },
        400: {
            'description': 'Error en los datos enviados o nombre de usuario duplicado'
        }
    }
})
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
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Actualizar un usuario existente',
    'description': 'Modifica los datos de un usuario específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario a modificar'
        },
        {
            'name': 'usuario',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Nombre de usuario único'},
                    'password': {'type': 'string', 'description': 'Contraseña del usuario'},
                    'nombre_completo': {'type': 'string', 'description': 'Nombre y apellidos del usuario'},
                    'rol': {'type': 'string', 'description': 'Rol del usuario', 'enum': ['administrador', 'supervisor', 'técnico', 'recepcionista']},
                    'activo': {'type': 'boolean', 'description': 'Estado de la cuenta'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Usuario actualizado correctamente',
            'schema': {'$ref': '#/definitions/Usuario'}
        },
        400: {
            'description': 'Error en los datos enviados o nombre de usuario duplicado'
        },
        404: {
            'description': 'Usuario no encontrado'
        }
    }
})
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
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Eliminar un usuario',
    'description': 'Elimina permanentemente un usuario del sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Usuario eliminado correctamente (sin contenido)'
        },
        404: {
            'description': 'Usuario no encontrado'
        }
    }
})
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    
    return '', 204

# Cambiar contraseña
@usuario_bp.route('/<int:id>/cambiar-password', methods=['PUT'])
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Cambiar contraseña',
    'description': 'Permite a un usuario cambiar su contraseña (requiere contraseña actual)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario'
        },
        {
            'name': 'datos',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'password_actual': {'type': 'string', 'description': 'Contraseña actual del usuario'},
                    'password_nueva': {'type': 'string', 'description': 'Nueva contraseña'}
                },
                'required': ['password_actual', 'password_nueva']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Contraseña cambiada correctamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'mensaje': {'type': 'string', 'example': 'Contraseña cambiada correctamente'}
                }
            }
        },
        400: {
            'description': 'Faltan parámetros necesarios'
        },
        401: {
            'description': 'La contraseña actual es incorrecta'
        },
        404: {
            'description': 'Usuario no encontrado'
        }
    }
})
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
@swag_from({
    'tags': ['usuarios'],
    'summary': 'Activar/desactivar un usuario',
    'description': 'Cambia el estado de activación de un usuario (habilitar/deshabilitar cuenta)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del usuario'
        }
    ],
    'responses': {
        200: {
            'description': 'Estado del usuario modificado correctamente',
            'schema': {'$ref': '#/definitions/Usuario'}
        },
        404: {
            'description': 'Usuario no encontrado'
        }
    }
})
def toggle_activo(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    return jsonify(usuario.to_dict())