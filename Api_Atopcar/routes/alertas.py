from flask import Blueprint, request, jsonify
from extensions import db
from models.alerta import Alerta
from models.tag import Tag
from models.vehiculo import Vehiculo
from flasgger import swag_from

# Crear el blueprint para las alertas
alerta_bp = Blueprint('alertas', __name__, url_prefix='/api/alertas')

# Obtener todas las alertas
@alerta_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Obtener todas las alertas',
    'description': 'Obtiene la lista completa de alertas con opción de filtrar por estado de lectura',
    'parameters': [
        {
            'name': 'leido',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar por estado de lectura (true/false)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de alertas',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Alerta'}
            }
        }
    }
})
def get_all_alertas():
    # Opcionalmente filtrar por leídas/no leídas
    leido = request.args.get('leido')
    if leido is not None:
        leido_bool = leido.lower() == 'true'
        alertas = Alerta.query.filter_by(leido=leido_bool).all()
    else:
        alertas = Alerta.query.all()
    
    return jsonify([alerta.to_dict() for alerta in alertas])

# Obtener una alerta específica
@alerta_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Obtener una alerta específica',
    'description': 'Obtiene los detalles de una alerta por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la alerta'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles de la alerta',
            'schema': {'$ref': '#/definitions/Alerta'}
        },
        404: {
            'description': 'Alerta no encontrada'
        }
    }
})
def get_alerta(id):
    alerta = Alerta.query.get_or_404(id)
    return jsonify(alerta.to_dict())

# Crear una nueva alerta
@alerta_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Crear una nueva alerta',
    'description': 'Registra una nueva alerta en el sistema',
    'parameters': [
        {
            'name': 'alerta',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag asociado'},
                    'vehiculo_id': {'type': 'integer', 'description': 'ID del vehículo asociado'},
                    'tipo': {'type': 'string', 'enum': ['bateria_baja', 'fuera_de_zona', 'movimiento_no_autorizado', 'averia', 'otros']},
                    'descripcion': {'type': 'string', 'description': 'Detalle de la alerta'},
                    'leido': {'type': 'boolean', 'default': False}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Alerta creada exitosamente',
            'schema': {'$ref': '#/definitions/Alerta'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_alerta():
    data = request.json
    
    # Verificar que existen las relaciones si se proporcionan
    if data.get('tag_id') and not Tag.query.get(data['tag_id']):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    if data.get('vehiculo_id') and not Vehiculo.query.get(data['vehiculo_id']):
        return jsonify({"error": "El vehículo especificado no existe"}), 400
    
    nueva_alerta = Alerta(
        tag_id=data.get('tag_id'),
        vehiculo_id=data.get('vehiculo_id'),
        tipo=data.get('tipo', 'otros'),
        descripcion=data.get('descripcion'),
        leido=data.get('leido', False)
    )
    
    db.session.add(nueva_alerta)
    db.session.commit()
    
    return jsonify(nueva_alerta.to_dict()), 201

# Actualizar una alerta
@alerta_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Actualizar una alerta existente',
    'description': 'Modifica los datos de una alerta específica',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la alerta a modificar'
        },
        {
            'name': 'alerta',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag asociado'},
                    'vehiculo_id': {'type': 'integer', 'description': 'ID del vehículo asociado'},
                    'tipo': {'type': 'string', 'enum': ['bateria_baja', 'fuera_de_zona', 'movimiento_no_autorizado', 'averia', 'otros']},
                    'descripcion': {'type': 'string', 'description': 'Detalle de la alerta'},
                    'leido': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Alerta actualizada correctamente',
            'schema': {'$ref': '#/definitions/Alerta'}
        },
        404: {
            'description': 'Alerta no encontrada'
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def update_alerta(id):
    alerta = Alerta.query.get_or_404(id)
    data = request.json
    
    # Verificar que existen las relaciones si se actualizan
    if 'tag_id' in data and data['tag_id'] is not None and not Tag.query.get(data['tag_id']):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    if 'vehiculo_id' in data and data['vehiculo_id'] is not None and not Vehiculo.query.get(data['vehiculo_id']):
        return jsonify({"error": "El vehículo especificado no existe"}), 400
    
    # Actualizar campos
    if 'tag_id' in data:
        alerta.tag_id = data['tag_id']
    if 'vehiculo_id' in data:
        alerta.vehiculo_id = data['vehiculo_id']
    if 'tipo' in data:
        alerta.tipo = data['tipo']
    if 'descripcion' in data:
        alerta.descripcion = data['descripcion']
    if 'leido' in data:
        alerta.leido = data['leido']
    
    db.session.commit()
    
    return jsonify(alerta.to_dict())

# Eliminar una alerta
@alerta_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Eliminar una alerta',
    'description': 'Elimina permanentemente una alerta del sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la alerta a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Alerta eliminada correctamente (sin contenido)'
        },
        404: {
            'description': 'Alerta no encontrada'
        }
    }
})
def delete_alerta(id):
    alerta = Alerta.query.get_or_404(id)
    db.session.delete(alerta)
    db.session.commit()
    
    return '', 204

# Marcar una alerta como leída
@alerta_bp.route('/<int:id>/marcar-leida', methods=['PUT'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Marcar alerta como leída',
    'description': 'Actualiza el estado de una alerta específica a "leída"',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la alerta a marcar como leída'
        }
    ],
    'responses': {
        200: {
            'description': 'Alerta marcada como leída',
            'schema': {'$ref': '#/definitions/Alerta'}
        },
        404: {
            'description': 'Alerta no encontrada'
        }
    }
})
def marcar_leida(id):
    alerta = Alerta.query.get_or_404(id)
    alerta.leido = True
    db.session.commit()
    
    return jsonify(alerta.to_dict())

# Obtener alertas no leídas
@alerta_bp.route('/no-leidas', methods=['GET'])
@swag_from({
    'tags': ['alertas'],
    'summary': 'Obtener alertas no leídas',
    'description': 'Recupera todas las alertas pendientes que no han sido marcadas como leídas',
    'responses': {
        200: {
            'description': 'Lista de alertas no leídas',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Alerta'}
            }
        }
    }
})
def get_no_leidas():
    alertas_no_leidas = Alerta.query.filter_by(leido=False).all()
    return jsonify([alerta.to_dict() for alerta in alertas_no_leidas])