from flask import Blueprint, request, jsonify
from extensions import db
from models.taller import Taller
from models.zona import Zona
from models.anchor import Anchor
from sqlalchemy import func
from flasgger import swag_from

# Crear el blueprint para los talleres
taller_bp = Blueprint('talleres', __name__, url_prefix='/api/talleres')

# Obtener todos los talleres
@taller_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Obtener todos los talleres',
    'description': 'Recupera la lista completa de talleres registrados en el sistema',
    'responses': {
        200: {
            'description': 'Lista de talleres',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Taller'}
            }
        }
    }
})
def get_all_talleres():
    talleres = Taller.query.all()
    return jsonify([taller.to_dict() for taller in talleres])

# Obtener un taller específico
@taller_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Obtener un taller específico',
    'description': 'Recupera los detalles de un taller por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles del taller',
            'schema': {'$ref': '#/definitions/Taller'}
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def get_taller(id):
    taller = Taller.query.get_or_404(id)
    return jsonify(taller.to_dict())

# Crear un nuevo taller
@taller_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Crear un nuevo taller',
    'description': 'Registra un nuevo taller en el sistema',
    'parameters': [
        {
            'name': 'taller',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'description': 'Nombre del taller o instalación'},
                    'svg_plano': {'type': 'string', 'description': 'Representación SVG del plano del taller'}
                },
                'required': ['nombre']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Taller creado exitosamente',
            'schema': {'$ref': '#/definitions/Taller'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_taller():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('nombre'):
        return jsonify({"error": "El nombre del taller es obligatorio"}), 400
    
    nuevo_taller = Taller(
        nombre=data['nombre'],
        svg_plano=data.get('svg_plano')
    )
    
    db.session.add(nuevo_taller)
    db.session.commit()
    
    return jsonify(nuevo_taller.to_dict()), 201

# Actualizar un taller
@taller_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Actualizar un taller existente',
    'description': 'Modifica los datos de un taller específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller a modificar'
        },
        {
            'name': 'taller',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'description': 'Nombre del taller o instalación'},
                    'svg_plano': {'type': 'string', 'description': 'Representación SVG del plano del taller'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Taller actualizado correctamente',
            'schema': {'$ref': '#/definitions/Taller'}
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def update_taller(id):
    taller = Taller.query.get_or_404(id)
    data = request.json
    
    # Actualizar campos
    if 'nombre' in data:
        taller.nombre = data['nombre']
    if 'svg_plano' in data:
        taller.svg_plano = data['svg_plano']
    
    db.session.commit()
    
    return jsonify(taller.to_dict())

# Eliminar un taller
@taller_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Eliminar un taller',
    'description': 'Elimina permanentemente un taller del sistema si no tiene elementos asociados',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Taller eliminado correctamente (sin contenido)'
        },
        400: {
            'description': 'No se puede eliminar el taller porque tiene elementos asociados'
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def delete_taller(id):
    taller = Taller.query.get_or_404(id)
    
    # Verificar si tiene zonas o anchors asociados
    zonas_count = Zona.query.filter_by(taller_id=id).count()
    anchors_count = Anchor.query.filter_by(taller_id=id).count()
    
    if zonas_count > 0 or anchors_count > 0:
        return jsonify({
            "error": "No se puede eliminar el taller porque tiene elementos asociados", 
            "zonas": zonas_count, 
            "anchors": anchors_count
        }), 400
    
    db.session.delete(taller)
    db.session.commit()
    
    return '', 204

# Obtener todas las zonas de un taller
@taller_bp.route('/<int:id>/zonas', methods=['GET'])
@swag_from({
    'tags': ['talleres', 'zonas'],
    'summary': 'Obtener zonas de un taller',
    'description': 'Recupera todas las zonas asociadas a un taller específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de zonas del taller',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Zona'}
            }
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def get_taller_zonas(id):
    # Verificar que el taller existe
    Taller.query.get_or_404(id)
    
    zonas = Zona.query.filter_by(taller_id=id).all()
    return jsonify([zona.to_dict() for zona in zonas])

# Obtener todos los anchors de un taller
@taller_bp.route('/<int:id>/anchors', methods=['GET'])
@swag_from({
    'tags': ['talleres', 'anchors'],
    'summary': 'Obtener anchors de un taller',
    'description': 'Recupera todos los dispositivos UWB fijos asociados a un taller',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller'
        },
        {
            'name': 'activo',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Filtrar por estado activo/inactivo (true/false)'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de anchors del taller',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Anchor'}
            }
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def get_taller_anchors(id):
    # Verificar que el taller existe
    Taller.query.get_or_404(id)
    
    # Filtrar anchors activos si se especifica
    activo = request.args.get('activo')
    
    query = Anchor.query.filter_by(taller_id=id)
    
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        query = query.filter_by(activo=activo_bool)
    
    anchors = query.all()
    return jsonify([anchor.to_dict() for anchor in anchors])

# Obtener estadísticas del taller
@taller_bp.route('/<int:id>/stats', methods=['GET'])
@swag_from({
    'tags': ['talleres'],
    'summary': 'Obtener estadísticas del taller',
    'description': 'Recupera información estadística sobre un taller específico',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del taller'
        }
    ],
    'responses': {
        200: {
            'description': 'Estadísticas del taller',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': 'ID del taller'},
                    'zonas': {'type': 'integer', 'description': 'Número de zonas'},
                    'anchors': {
                        'type': 'object',
                        'properties': {
                            'total': {'type': 'integer', 'description': 'Número total de anchors'},
                            'activos': {'type': 'integer', 'description': 'Número de anchors activos'},
                            'inactivos': {'type': 'integer', 'description': 'Número de anchors inactivos'}
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Taller no encontrado'
        }
    }
})
def get_taller_stats(id):
    # Verificar que el taller existe
    Taller.query.get_or_404(id)
    
    num_zonas = Zona.query.filter_by(taller_id=id).count()
    num_anchors = Anchor.query.filter_by(taller_id=id).count()
    num_anchors_activos = Anchor.query.filter_by(taller_id=id, activo=True).count()
    
    return jsonify({
        'id': id,
        'zonas': num_zonas,
        'anchors': {
            'total': num_anchors,
            'activos': num_anchors_activos,
            'inactivos': num_anchors - num_anchors_activos
        }
    })