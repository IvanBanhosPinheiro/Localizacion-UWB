from flask import Blueprint, request, jsonify
from extensions import db
from models.anchor import Anchor
from models.taller import Taller
from models.zona import Zona
from flasgger import swag_from

# Crear el blueprint para los anchors
anchor_bp = Blueprint('anchors', __name__, url_prefix='/api/anchors')

# Obtener todos los anchors
@anchor_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Obtener todos los anchors',
    'description': 'Recupera la lista de todos los dispositivos UWB fijos con opciones de filtrado',
    'parameters': [
        {
            'name': 'taller_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por ID del taller'
        },
        {
            'name': 'zona_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por ID de zona'
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
            'description': 'Lista de anchors',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Anchor'}
            }
        }
    }
})
def get_all_anchors():
    # Filtrar por taller_id si se proporciona
    taller_id = request.args.get('taller_id', type=int)
    # Filtrar por zona_id si se proporciona
    zona_id = request.args.get('zona_id', type=int)
    # Filtrar por activo
    activo = request.args.get('activo')
    
    query = Anchor.query
    
    if taller_id:
        query = query.filter_by(taller_id=taller_id)
    if zona_id:
        query = query.filter_by(zona_id=zona_id)
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        query = query.filter_by(activo=activo_bool)
    
    anchors = query.all()
    return jsonify([anchor.to_dict() for anchor in anchors])

# Obtener un anchor específico
@anchor_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Obtener un anchor específico',
    'description': 'Recupera los detalles de un dispositivo UWB fijo por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del anchor'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles del anchor',
            'schema': {'$ref': '#/definitions/Anchor'}
        },
        404: {
            'description': 'Anchor no encontrado'
        }
    }
})
def get_anchor(id):
    anchor = Anchor.query.get_or_404(id)
    return jsonify(anchor.to_dict())

# Crear un nuevo anchor
@anchor_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Crear un nuevo anchor',
    'description': 'Registra un nuevo dispositivo UWB fijo en el sistema',
    'parameters': [
        {
            'name': 'anchor',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'description': 'Nombre descriptivo del anchor'},
                    'mac': {'type': 'string', 'description': 'Dirección MAC única del dispositivo'},
                    'x': {'type': 'integer', 'description': 'Coordenada X en el plano del taller'},
                    'y': {'type': 'integer', 'description': 'Coordenada Y en el plano del taller'},
                    'canal_rf': {'type': 'string', 'description': 'Canal de radiofrecuencia'},
                    'zona_id': {'type': 'integer', 'description': 'ID de la zona donde está instalado'},
                    'taller_id': {'type': 'integer', 'description': 'ID del taller donde está instalado'},
                    'activo': {'type': 'boolean', 'description': 'Estado operativo del anchor', 'default': True}
                },
                'required': ['mac']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Anchor creado exitosamente',
            'schema': {'$ref': '#/definitions/Anchor'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_anchor():
    data = request.json
    
    # Verificar que existen las relaciones si se proporcionan
    if data.get('taller_id') and not Taller.query.get(data['taller_id']):
        return jsonify({"error": "El taller especificado no existe"}), 400
    
    if data.get('zona_id') and not Zona.query.get(data['zona_id']):
        return jsonify({"error": "La zona especificada no existe"}), 400
    
    # Verificar que la MAC sea única
    if data.get('mac') and Anchor.query.filter_by(mac=data['mac']).first():
        return jsonify({"error": "La dirección MAC ya está registrada para otro anchor"}), 400
    
    nuevo_anchor = Anchor(
        nombre=data.get('nombre'),
        mac=data.get('mac'),
        x=data.get('x'),
        y=data.get('y'),
        canal_rf=data.get('canal_rf'),
        zona_id=data.get('zona_id'),
        taller_id=data.get('taller_id'),
        activo=data.get('activo', True)
    )
    
    db.session.add(nuevo_anchor)
    db.session.commit()
    
    return jsonify(nuevo_anchor.to_dict()), 201

# Actualizar un anchor
@anchor_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Actualizar un anchor existente',
    'description': 'Modifica los datos de un dispositivo UWB fijo',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del anchor a modificar'
        },
        {
            'name': 'anchor',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'description': 'Nombre descriptivo del anchor'},
                    'mac': {'type': 'string', 'description': 'Dirección MAC única del dispositivo'},
                    'x': {'type': 'integer', 'description': 'Coordenada X en el plano del taller'},
                    'y': {'type': 'integer', 'description': 'Coordenada Y en el plano del taller'},
                    'canal_rf': {'type': 'string', 'description': 'Canal de radiofrecuencia'},
                    'zona_id': {'type': 'integer', 'description': 'ID de la zona donde está instalado'},
                    'taller_id': {'type': 'integer', 'description': 'ID del taller donde está instalado'},
                    'activo': {'type': 'boolean', 'description': 'Estado operativo del anchor'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Anchor actualizado correctamente',
            'schema': {'$ref': '#/definitions/Anchor'}
        },
        404: {
            'description': 'Anchor no encontrado'
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def update_anchor(id):
    anchor = Anchor.query.get_or_404(id)
    data = request.json
    
    # Verificar que existen las relaciones si se actualizan
    if 'taller_id' in data and data['taller_id'] is not None and not Taller.query.get(data['taller_id']):
        return jsonify({"error": "El taller especificado no existe"}), 400
    
    if 'zona_id' in data and data['zona_id'] is not None and not Zona.query.get(data['zona_id']):
        return jsonify({"error": "La zona especificada no existe"}), 400
    
    # Verificar que la MAC sea única si se actualiza
    if 'mac' in data and data['mac'] != anchor.mac:
        if Anchor.query.filter_by(mac=data['mac']).first():
            return jsonify({"error": "La dirección MAC ya está registrada para otro anchor"}), 400
    
    # Actualizar campos
    if 'nombre' in data:
        anchor.nombre = data['nombre']
    if 'mac' in data:
        anchor.mac = data['mac']
    if 'x' in data:
        anchor.x = data['x']
    if 'y' in data:
        anchor.y = data['y']
    if 'canal_rf' in data:
        anchor.canal_rf = data['canal_rf']
    if 'zona_id' in data:
        anchor.zona_id = data['zona_id']
    if 'taller_id' in data:
        anchor.taller_id = data['taller_id']
    if 'activo' in data:
        anchor.activo = data['activo']
    
    db.session.commit()
    
    return jsonify(anchor.to_dict())

# Eliminar un anchor
@anchor_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Eliminar un anchor',
    'description': 'Elimina permanentemente un dispositivo UWB fijo del sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del anchor a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Anchor eliminado correctamente (sin contenido)'
        },
        404: {
            'description': 'Anchor no encontrado'
        }
    }
})
def delete_anchor(id):
    anchor = Anchor.query.get_or_404(id)
    db.session.delete(anchor)
    db.session.commit()
    
    return '', 204

# Activar/desactivar un anchor
@anchor_bp.route('/<int:id>/toggle-activo', methods=['PUT'])
@swag_from({
    'tags': ['anchors'],
    'summary': 'Activar/desactivar un anchor',
    'description': 'Cambia el estado de activación de un anchor (on/off)',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del anchor a cambiar su estado'
        }
    ],
    'responses': {
        200: {
            'description': 'Estado del anchor modificado correctamente',
            'schema': {'$ref': '#/definitions/Anchor'}
        },
        404: {
            'description': 'Anchor no encontrado'
        }
    }
})
def toggle_activo(id):
    anchor = Anchor.query.get_or_404(id)
    anchor.activo = not anchor.activo
    db.session.commit()
    
    return jsonify(anchor.to_dict())