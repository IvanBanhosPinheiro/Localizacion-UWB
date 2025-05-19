from flask import Blueprint, request, jsonify
from extensions import db
from models.tag import Tag
from models.vehiculo import Vehiculo
from datetime import datetime
from flasgger import swag_from

# Crear el blueprint para los tags
tag_bp = Blueprint('tags', __name__, url_prefix='/api/tags')

# Obtener todos los tags
@tag_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Obtener todos los tags',
    'description': 'Recupera la lista de todos los dispositivos UWB móviles con opciones de filtrado',
    'parameters': [
        {
            'name': 'estado',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrar por estado del tag (libre, asignado, averiado, baja, mantenimiento)'
        },
        {
            'name': 'bateria_baja',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar tags con batería baja (true/false)'
        },
        {
            'name': 'asignado',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar tags asignados o no asignados a vehículos (true/false)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de tags',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Tag'}
            }
        }
    }
})
def get_all_tags():
    # Filtrar por estado si se especifica
    estado = request.args.get('estado')
    # Filtrar por batería baja
    bateria_baja = request.args.get('bateria_baja')
    # Filtrar tags asignados o no asignados
    asignado = request.args.get('asignado')
    
    query = Tag.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    if bateria_baja is not None:
        if bateria_baja.lower() == 'true':
            query = query.filter(Tag.bateria < 20)  # Considerar baja a menos del 20%
    
    tags = query.all()
    
    if asignado is not None:
        asignado_bool = asignado.lower() == 'true'
        # Filtrar en memoria ya que necesitamos acceder a la relación
        if asignado_bool:
            tags = [tag for tag in tags if tag.vehiculo is not None]
        else:
            tags = [tag for tag in tags if tag.vehiculo is None]
    
    return jsonify([tag.to_dict() for tag in tags])

# Obtener un tag específico
@tag_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Obtener un tag específico',
    'description': 'Recupera los detalles de un tag por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles del tag',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Tag no encontrado'
        }
    }
})
def get_tag(id):
    tag = Tag.query.get_or_404(id)
    return jsonify(tag.to_dict())

# Crear un nuevo tag
@tag_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Crear un nuevo tag',
    'description': 'Registra un nuevo dispositivo UWB móvil en el sistema',
    'parameters': [
        {
            'name': 'tag',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'codigo': {'type': 'string', 'description': 'Código único del tag'},
                    'mac': {'type': 'string', 'description': 'Dirección MAC única del dispositivo'},
                    'estado': {'type': 'string', 'description': 'Estado del tag', 'enum': ['libre', 'asignado', 'averiado', 'baja', 'mantenimiento'], 'default': 'libre'},
                    'bateria': {'type': 'integer', 'description': 'Nivel de batería en porcentaje'},
                    'observaciones': {'type': 'string', 'description': 'Notas adicionales'}
                },
                'required': ['codigo', 'mac']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Tag creado exitosamente',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_tag():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('codigo') or not data.get('mac'):
        return jsonify({"error": "El código y la MAC son obligatorios"}), 400
    
    # Verificar que el código y la MAC sean únicos
    if Tag.query.filter_by(codigo=data['codigo']).first():
        return jsonify({"error": f"Ya existe un tag con el código {data['codigo']}"}), 400
    
    if Tag.query.filter_by(mac=data['mac']).first():
        return jsonify({"error": f"Ya existe un tag con la MAC {data['mac']}"}), 400
    
    nuevo_tag = Tag(
        codigo=data['codigo'],
        mac=data['mac'],
        estado=data.get('estado', 'libre'),
        bateria=data.get('bateria'),
        ultima_comunicacion=datetime.utcnow(),
        observaciones=data.get('observaciones')
    )
    
    db.session.add(nuevo_tag)
    db.session.commit()
    
    return jsonify(nuevo_tag.to_dict()), 201

# Actualizar un tag
@tag_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Actualizar un tag existente',
    'description': 'Modifica los datos de un dispositivo UWB móvil',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag a modificar'
        },
        {
            'name': 'tag',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'codigo': {'type': 'string', 'description': 'Código único del tag'},
                    'mac': {'type': 'string', 'description': 'Dirección MAC única del dispositivo'},
                    'estado': {'type': 'string', 'description': 'Estado del tag', 'enum': ['libre', 'asignado', 'averiado', 'baja', 'mantenimiento']},
                    'bateria': {'type': 'integer', 'description': 'Nivel de batería en porcentaje'},
                    'observaciones': {'type': 'string', 'description': 'Notas adicionales'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Tag actualizado correctamente',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Tag no encontrado'
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def update_tag(id):
    tag = Tag.query.get_or_404(id)
    data = request.json
    
    # Verificar que el código sea único si se cambia
    if 'codigo' in data and data['codigo'] != tag.codigo:
        if Tag.query.filter_by(codigo=data['codigo']).first():
            return jsonify({"error": f"Ya existe un tag con el código {data['codigo']}"}), 400
    
    # Verificar que la MAC sea única si se cambia
    if 'mac' in data and data['mac'] != tag.mac:
        if Tag.query.filter_by(mac=data['mac']).first():
            return jsonify({"error": f"Ya existe un tag con la MAC {data['mac']}"}), 400
    
    # Actualizar campos
    if 'codigo' in data:
        tag.codigo = data['codigo']
    if 'mac' in data:
        tag.mac = data['mac']
    if 'estado' in data:
        tag.estado = data['estado']
    if 'bateria' in data:
        tag.bateria = data['bateria']
    if 'observaciones' in data:
        tag.observaciones = data['observaciones']
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Eliminar un tag
@tag_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Eliminar un tag',
    'description': 'Elimina permanentemente un tag del sistema (solo si no está asignado)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Tag eliminado correctamente (sin contenido)'
        },
        404: {
            'description': 'Tag no encontrado'
        },
        400: {
            'description': 'No se puede eliminar el tag porque está asignado'
        }
    }
})
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    # Verificar si el tag está asignado a un vehículo
    if tag.vehiculo:
        return jsonify({"error": "No se puede eliminar un tag asignado a un vehículo. Desasigne primero el tag."}), 400
    
    db.session.delete(tag)
    db.session.commit()
    
    return '', 204

# Asignar un tag a un vehículo
@tag_bp.route('/<int:id>/asignar/<int:vehiculo_id>', methods=['PUT'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Asignar un tag a un vehículo',
    'description': 'Vincula un tag con un vehículo para su seguimiento',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag'
        },
        {
            'name': 'vehiculo_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo al que se asignará el tag'
        }
    ],
    'responses': {
        200: {
            'description': 'Tag asignado correctamente',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Tag o vehículo no encontrado'
        },
        400: {
            'description': 'El tag ya está asignado o el vehículo ya tiene un tag'
        }
    }
})
def asignar_vehiculo(id, vehiculo_id):
    tag = Tag.query.get_or_404(id)
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    
    # Verificar que el tag no esté ya asignado
    if tag.vehiculo:
        return jsonify({"error": f"El tag ya está asignado al vehículo {tag.vehiculo.id}"}), 400
    
    # Verificar que el vehículo no tenga ya un tag asignado
    if Vehiculo.query.filter(Vehiculo.tag != None).filter_by(id=vehiculo_id).first():
        return jsonify({"error": "El vehículo ya tiene un tag asignado"}), 400
    
    # Asignar el tag al vehículo
    vehiculo.tag = tag
    tag.estado = 'asignado'
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Desasignar un tag de un vehículo
@tag_bp.route('/<int:id>/desasignar', methods=['PUT'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Desasignar un tag de un vehículo',
    'description': 'Desvincula un tag del vehículo al que está asociado',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag a desasignar'
        }
    ],
    'responses': {
        200: {
            'description': 'Tag desasignado correctamente',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Tag no encontrado'
        },
        400: {
            'description': 'El tag no está asignado a ningún vehículo'
        }
    }
})
def desasignar_vehiculo(id):
    tag = Tag.query.get_or_404(id)
    
    # Verificar que el tag esté asignado
    if not tag.vehiculo:
        return jsonify({"error": "El tag no está asignado a ningún vehículo"}), 400
    
    # Desasignar el tag
    tag.vehiculo = None
    tag.estado = 'libre'
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Actualizar el nivel de batería de un tag
@tag_bp.route('/<int:id>/bateria', methods=['PUT'])
@swag_from({
    'tags': ['tags'],
    'summary': 'Actualizar nivel de batería',
    'description': 'Actualiza el nivel de batería y la última comunicación de un tag',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag'
        },
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'bateria': {'type': 'integer', 'description': 'Nuevo nivel de batería en porcentaje'}
                },
                'required': ['bateria']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Batería actualizada correctamente',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Tag no encontrado'
        },
        400: {
            'description': 'No se ha especificado el nivel de batería'
        }
    }
})
def update_bateria(id):
    tag = Tag.query.get_or_404(id)
    data = request.json
    
    if 'bateria' not in data:
        return jsonify({"error": "No se ha especificado el nivel de batería"}), 400
    
    tag.bateria = data['bateria']
    tag.ultima_comunicacion = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(tag.to_dict())