from flask import Blueprint, request, jsonify
from extensions import db
from models.vehiculo import Vehiculo
from models.tag import Tag
from flasgger import swag_from

# Crear el blueprint para los vehículos
vehiculo_bp = Blueprint('vehiculos', __name__, url_prefix='/api/vehiculos')

# Obtener todos los vehículos
@vehiculo_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Obtener todos los vehículos',
    'description': 'Recupera la lista completa de vehículos con opciones de filtrado',
    'parameters': [
        {
            'name': 'estado',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrar por estado (activo, pendiente, finalizado, entregado)'
        },
        {
            'name': 'con_tag',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar vehículos con o sin tag asignado (true/false)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de vehículos',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Vehiculo'}
            }
        }
    }
})
def get_all_vehiculos():
    # Filtrar por estado si se especifica
    estado = request.args.get('estado')
    # Filtrar vehículos con/sin tag
    con_tag = request.args.get('con_tag')
    
    query = Vehiculo.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    vehiculos = query.all()
    
    # Filtrar por vehículos con tag o sin tag
    if con_tag is not None:
        con_tag_bool = con_tag.lower() == 'true'
        if con_tag_bool:
            vehiculos = [v for v in vehiculos if hasattr(v, 'tag') and v.tag]
        else:
            vehiculos = [v for v in vehiculos if not hasattr(v, 'tag') or not v.tag]
    
    return jsonify([vehiculo.to_dict() for vehiculo in vehiculos])

# Obtener un vehículo específico
@vehiculo_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Obtener un vehículo específico',
    'description': 'Recupera los detalles de un vehículo por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles del vehículo',
            'schema': {'$ref': '#/definitions/Vehiculo'}
        },
        404: {
            'description': 'Vehículo no encontrado'
        }
    }
})
def get_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    return jsonify(vehiculo.to_dict())

# Crear un nuevo vehículo
@vehiculo_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Crear un nuevo vehículo',
    'description': 'Registra un nuevo vehículo en el sistema',
    'parameters': [
        {
            'name': 'vehiculo',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'matricula': {'type': 'string', 'description': 'Matrícula o placa del vehículo'},
                    'bastidor': {'type': 'string', 'description': 'Número de bastidor o VIN único del vehículo'},
                    'referencia': {'type': 'string', 'description': 'Referencia interna o descripción del vehículo'},
                    'estado': {'type': 'string', 'description': 'Estado del vehículo', 'enum': ['activo', 'pendiente', 'finalizado', 'entregado'], 'default': 'activo'}
                },
                'example': {
                    'matricula': '1234ABC',
                    'bastidor': 'VF12345678',
                    'referencia': 'Seat Ibiza azul',
                    'estado': 'activo'
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Vehículo creado exitosamente',
            'schema': {'$ref': '#/definitions/Vehiculo'}
        },
        400: {
            'description': 'Error en los datos enviados o bastidor duplicado'
        }
    }
})
def create_vehiculo():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('matricula') and not data.get('bastidor'):
        return jsonify({"error": "Se requiere al menos matrícula o bastidor"}), 400
    
    # Verificar que el bastidor sea único si se proporciona
    if data.get('bastidor') and Vehiculo.query.filter_by(bastidor=data['bastidor']).first():
        return jsonify({"error": f"Ya existe un vehículo con el bastidor {data['bastidor']}"}), 400
    
    nuevo_vehiculo = Vehiculo(
        matricula=data.get('matricula'),
        bastidor=data.get('bastidor'),
        referencia=data.get('referencia'),
        estado=data.get('estado', 'activo')
    )
    
    db.session.add(nuevo_vehiculo)
    db.session.commit()
    
    return jsonify(nuevo_vehiculo.to_dict()), 201

# Actualizar un vehículo
@vehiculo_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Actualizar un vehículo existente',
    'description': 'Modifica los datos de un vehículo específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo a modificar'
        },
        {
            'name': 'vehiculo',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'matricula': {'type': 'string', 'description': 'Matrícula o placa del vehículo'},
                    'bastidor': {'type': 'string', 'description': 'Número de bastidor o VIN único del vehículo'},
                    'referencia': {'type': 'string', 'description': 'Referencia interna o descripción del vehículo'},
                    'estado': {'type': 'string', 'description': 'Estado del vehículo', 'enum': ['activo', 'pendiente', 'finalizado', 'entregado']}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Vehículo actualizado correctamente',
            'schema': {'$ref': '#/definitions/Vehiculo'}
        },
        400: {
            'description': 'Error en los datos enviados o bastidor duplicado'
        },
        404: {
            'description': 'Vehículo no encontrado'
        }
    }
})
def update_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    data = request.json
    
    # Verificar que el bastidor sea único si se cambia
    if 'bastidor' in data and data['bastidor'] != vehiculo.bastidor:
        if data['bastidor'] and Vehiculo.query.filter_by(bastidor=data['bastidor']).first():
            return jsonify({"error": f"Ya existe un vehículo con el bastidor {data['bastidor']}"}), 400
    
    # Actualizar campos
    if 'matricula' in data:
        vehiculo.matricula = data['matricula']
    if 'bastidor' in data:
        vehiculo.bastidor = data['bastidor']
    if 'referencia' in data:
        vehiculo.referencia = data['referencia']
    if 'estado' in data:
        vehiculo.estado = data['estado']
    
    db.session.commit()
    
    return jsonify(vehiculo.to_dict())

# Eliminar un vehículo
@vehiculo_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Eliminar un vehículo',
    'description': 'Elimina permanentemente un vehículo del sistema (siempre que no tenga tag asignado)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Vehículo eliminado correctamente (sin contenido)'
        },
        400: {
            'description': 'No se puede eliminar el vehículo porque tiene un tag asignado'
        },
        404: {
            'description': 'Vehículo no encontrado'
        }
    }
})
def delete_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    
    # Verificar si el vehículo tiene un tag asignado
    if hasattr(vehiculo, 'tag') and vehiculo.tag:
        return jsonify({"error": "No se puede eliminar un vehículo con un tag asignado. Desasigne primero el tag."}), 400
    
    db.session.delete(vehiculo)
    db.session.commit()
    
    return '', 204

# Cambiar el estado de un vehículo
@vehiculo_bp.route('/<int:id>/estado', methods=['PUT'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Cambiar el estado de un vehículo',
    'description': 'Actualiza el estado de un vehículo (activo, entregado, baja)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo'
        },
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'estado': {'type': 'string', 'description': 'Nuevo estado del vehículo', 'enum': ['activo', 'entregado', 'baja']}
                },
                'required': ['estado']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Estado actualizado correctamente',
            'schema': {'$ref': '#/definitions/Vehiculo'}
        },
        400: {
            'description': 'Estado no válido o falta el estado'
        },
        404: {
            'description': 'Vehículo no encontrado'
        }
    }
})
def cambiar_estado(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    data = request.json
    
    if not data.get('estado'):
        return jsonify({"error": "El estado es obligatorio"}), 400
    
    # Verificar que el estado sea válido
    if data['estado'] not in ['activo', 'entregado', 'baja']:
        return jsonify({"error": "Estado no válido. Debe ser 'activo', 'entregado' o 'baja'"}), 400
    
    vehiculo.estado = data['estado']
    db.session.commit()
    
    return jsonify(vehiculo.to_dict())

# Obtener el tag asociado a un vehículo
@vehiculo_bp.route('/<int:id>/tag', methods=['GET'])
@swag_from({
    'tags': ['vehiculos', 'tags'],
    'summary': 'Obtener tag asociado a un vehículo',
    'description': 'Recupera la información del tag UWB asociado a un vehículo específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del vehículo'
        }
    ],
    'responses': {
        200: {
            'description': 'Información del tag',
            'schema': {'$ref': '#/definitions/Tag'}
        },
        404: {
            'description': 'Vehículo no encontrado o no tiene tag asignado'
        }
    }
})
def get_vehiculo_tag(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    
    if not hasattr(vehiculo, 'tag') or not vehiculo.tag:
        return jsonify({"error": "El vehículo no tiene un tag asignado"}), 404
    
    return jsonify(vehiculo.tag.to_dict())

# Buscar vehículos por matrícula o bastidor
@vehiculo_bp.route('/buscar', methods=['GET'])
@swag_from({
    'tags': ['vehiculos'],
    'summary': 'Buscar vehículos',
    'description': 'Busca vehículos por matrícula, bastidor o referencia',
    'parameters': [
        {
            'name': 'termino',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Término de búsqueda (matrícula, bastidor o referencia)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de vehículos coincidentes',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Vehiculo'}
            }
        },
        400: {
            'description': 'Término de búsqueda no especificado'
        }
    }
})
def buscar_vehiculo():
    termino = request.args.get('termino')
    
    if not termino:
        return jsonify({"error": "El término de búsqueda es obligatorio"}), 400
    
    # Buscar vehículos que coincidan con el término en matrícula o bastidor
    vehiculos = Vehiculo.query.filter(
        (Vehiculo.matricula.like(f"%{termino}%")) |
        (Vehiculo.bastidor.like(f"%{termino}%")) |
        (Vehiculo.referencia.like(f"%{termino}%"))
    ).all()
    
    return jsonify([vehiculo.to_dict() for vehiculo in vehiculos])