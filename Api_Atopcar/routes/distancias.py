from flask import Blueprint, request, jsonify
from extensions import db
from models.distancia import Distancia
from models.tag import Tag
from models.anchor import Anchor
from datetime import datetime
from routes.posiciones import triangular_posicion 
from flasgger import swag_from

# Crear el blueprint para las distancias
distancia_bp = Blueprint('distancias', __name__, url_prefix='/api/distancias')

# Obtener todas las distancias
@distancia_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Obtener todas las distancias',
    'description': 'Recupera la lista de todas las mediciones de distancia entre tags y anchors con opción de filtrado',
    'parameters': [
        {
            'name': 'tag_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por ID del tag'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de mediciones de distancia',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Distancia'}
            }
        }
    }
})
def get_all_distancias():
    # Filtrar por tag_id si se proporciona
    tag_id = request.args.get('tag_id', type=int)
    
    query = Distancia.query
    
    if tag_id:
        query = query.filter_by(tag_id=tag_id)
    
    distancias = query.all()
    return jsonify([distancia.to_dict() for distancia in distancias])

# Obtener una distancia específica
@distancia_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Obtener una distancia específica',
    'description': 'Recupera los detalles de una medición de distancia por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la medición de distancia'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles de la medición de distancia',
            'schema': {'$ref': '#/definitions/Distancia'}
        },
        404: {
            'description': 'Medición no encontrada'
        }
    }
})
def get_distancia(id):
    distancia = Distancia.query.get_or_404(id)
    return jsonify(distancia.to_dict())

# Crear una nueva distancia
@distancia_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Crear una nueva medición de distancia',
    'description': 'Registra una nueva medición de distancia entre un tag y hasta tres anchors',
    'parameters': [
        {
            'name': 'distancia',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag UWB'},
                    'anchor1_id': {'type': 'integer', 'description': 'ID del primer anchor'},
                    'anchor1_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al primer anchor (cm)'},
                    'anchor2_id': {'type': 'integer', 'description': 'ID del segundo anchor'},
                    'anchor2_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al segundo anchor (cm)'},
                    'anchor3_id': {'type': 'integer', 'description': 'ID del tercer anchor'},
                    'anchor3_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al tercer anchor (cm)'}
                },
                'required': ['tag_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Distancia creada exitosamente',
            'schema': {'$ref': '#/definitions/Distancia'}
        },
        200: {
            'description': 'Distancia existente actualizada',
            'schema': {'$ref': '#/definitions/Distancia'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_distancia():
    data = request.json
    
    # Verificar que el tag existe
    if not Tag.query.get(data.get('tag_id')):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    # Verificar que los anchors existen
    if data.get('anchor1_id') and not Anchor.query.get(data['anchor1_id']):
        return jsonify({"error": "El anchor1 especificado no existe"}), 400
    
    if data.get('anchor2_id') and not Anchor.query.get(data['anchor2_id']):
        return jsonify({"error": "El anchor2 especificado no existe"}), 400
    
    if data.get('anchor3_id') and not Anchor.query.get(data['anchor3_id']):
        return jsonify({"error": "El anchor3 especificado no existe"}), 400
    
    # Verificar si ya existe una entrada para este tag
    existing = Distancia.query.filter_by(tag_id=data.get('tag_id')).first()
    if existing:
        # Si existe, actualizar en lugar de crear
        if data.get('anchor1_id'):
            existing.anchor1_id = data.get('anchor1_id')
        if 'anchor1_dist' in data:
            existing.anchor1_dist = data.get('anchor1_dist')
        if data.get('anchor2_id'):
            existing.anchor2_id = data.get('anchor2_id')
        if 'anchor2_dist' in data:
            existing.anchor2_dist = data.get('anchor2_dist')
        if data.get('anchor3_id'):
            existing.anchor3_id = data.get('anchor3_id')
        if 'anchor3_dist' in data:
            existing.anchor3_dist = data.get('anchor3_dist')
        
        db.session.commit()
        return jsonify(existing.to_dict()), 200
    
    # Si no existe, crear nueva distancia
    nueva_distancia = Distancia(
        tag_id=data.get('tag_id'),
        anchor1_id=data.get('anchor1_id'),
        anchor1_dist=data.get('anchor1_dist'),
        anchor2_id=data.get('anchor2_id'),
        anchor2_dist=data.get('anchor2_dist'),
        anchor3_id=data.get('anchor3_id'),
        anchor3_dist=data.get('anchor3_dist')
    )
    
    db.session.add(nueva_distancia)
    db.session.commit()
    
    # Calcular y guardar la posición mediante triangulación
    if (nueva_distancia.anchor1_id and nueva_distancia.anchor1_dist and
        nueva_distancia.anchor2_id and nueva_distancia.anchor2_dist and
        nueva_distancia.anchor3_id and nueva_distancia.anchor3_dist):
        
        triangular_posicion(
            nueva_distancia.tag_id,
            nueva_distancia.anchor1_id, nueva_distancia.anchor1_dist,
            nueva_distancia.anchor2_id, nueva_distancia.anchor2_dist,
            nueva_distancia.anchor3_id, nueva_distancia.anchor3_dist
        )
    
    return jsonify(nueva_distancia.to_dict()), 201

# Actualizar una distancia
@distancia_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Actualizar una medición de distancia',
    'description': 'Modifica los datos de una medición de distancia existente',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la medición de distancia'
        },
        {
            'name': 'distancia',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag UWB'},
                    'anchor1_id': {'type': 'integer', 'description': 'ID del primer anchor'},
                    'anchor1_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al primer anchor (cm)'},
                    'anchor2_id': {'type': 'integer', 'description': 'ID del segundo anchor'},
                    'anchor2_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al segundo anchor (cm)'},
                    'anchor3_id': {'type': 'integer', 'description': 'ID del tercer anchor'},
                    'anchor3_dist': {'type': 'number', 'format': 'float', 'description': 'Distancia al tercer anchor (cm)'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Distancia actualizada correctamente',
            'schema': {'$ref': '#/definitions/Distancia'}
        },
        404: {
            'description': 'Distancia no encontrada'
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def update_distancia(id):
    distancia = Distancia.query.get_or_404(id)
    data = request.json
    
    # Verificar que el tag existe si se cambia
    if 'tag_id' in data and not Tag.query.get(data['tag_id']):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    # Verificar que los anchors existen si se cambian
    if 'anchor1_id' in data and data['anchor1_id'] and not Anchor.query.get(data['anchor1_id']):
        return jsonify({"error": "El anchor1 especificado no existe"}), 400
    
    if 'anchor2_id' in data and data['anchor2_id'] and not Anchor.query.get(data['anchor2_id']):
        return jsonify({"error": "El anchor2 especificado no existe"}), 400
    
    if 'anchor3_id' in data and data['anchor3_id'] and not Anchor.query.get(data['anchor3_id']):
        return jsonify({"error": "El anchor3 especificado no existe"}), 400
    
    # Actualizar campos
    if 'tag_id' in data:
        distancia.tag_id = data['tag_id']
    if 'anchor1_id' in data:
        distancia.anchor1_id = data['anchor1_id']
    if 'anchor1_dist' in data:
        distancia.anchor1_dist = data['anchor1_dist']
    if 'anchor2_id' in data:
        distancia.anchor2_id = data['anchor2_id']
    if 'anchor2_dist' in data:
        distancia.anchor2_dist = data['anchor2_dist']
    if 'anchor3_id' in data:
        distancia.anchor3_id = data['anchor3_id']
    if 'anchor3_dist' in data:
        distancia.anchor3_dist = data['anchor3_dist']
    
    db.session.commit()
    
    # Calcular y guardar la posición mediante triangulación
    if (distancia.anchor1_id and distancia.anchor1_dist and
        distancia.anchor2_id and distancia.anchor2_dist and
        distancia.anchor3_id and distancia.anchor3_dist):
        
        triangular_posicion(
            distancia.tag_id,
            distancia.anchor1_id, distancia.anchor1_dist,
            distancia.anchor2_id, distancia.anchor2_dist,
            distancia.anchor3_id, distancia.anchor3_dist
        )
    
    return jsonify(distancia.to_dict())

# Eliminar una distancia
@distancia_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Eliminar una medición de distancia',
    'description': 'Elimina permanentemente una medición de distancia del sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la medición de distancia a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Distancia eliminada correctamente (sin contenido)'
        },
        404: {
            'description': 'Distancia no encontrada'
        }
    }
})
def delete_distancia(id):
    distancia = Distancia.query.get_or_404(id)
    db.session.delete(distancia)
    db.session.commit()
    
    return '', 204

# Obtener la última distancia para un tag específico
@distancia_bp.route('/tag/<int:tag_id>', methods=['GET'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Obtener distancia por tag',
    'description': 'Recupera la última medición de distancia para un tag específico',
    'parameters': [
        {
            'name': 'tag_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del tag'
        }
    ],
    'responses': {
        200: {
            'description': 'Medición de distancia para el tag',
            'schema': {'$ref': '#/definitions/Distancia'}
        },
        404: {
            'description': 'No se encontraron mediciones para este tag'
        }
    }
})
def get_by_tag(tag_id):
    distancia = Distancia.query.filter_by(tag_id=tag_id).first_or_404()
    return jsonify(distancia.to_dict())



# Registrar distancias desde un dispositivo
@distancia_bp.route('/registrar', methods=['POST'])
@swag_from({
    'tags': ['distancias'],
    'summary': 'Registrar distancias desde dispositivo',
    'description': 'Endpoint para recibir mediciones directamente desde dispositivos UWB',
    'parameters': [
        {
            'name': 'datos',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag': {'type': 'string', 'description': 'Código del tag UWB'},
                    'anchors': {
                        'type': 'array',
                        'description': 'Lista de anchors con sus distancias',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'shortAddres': {'type': 'string', 'description': 'Nombre del anchor'},
                                'distancia': {'type': 'string', 'description': 'Distancia en metros'}
                            }
                        }
                    }
                },
                'required': ['tag', 'anchors']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Distancias registradas correctamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'mensaje': {'type': 'string'},
                    'data': {'$ref': '#/definitions/Distancia'}
                }
            }
        },
        200: {
            'description': 'Distancias actualizadas o sin cambios significativos',
            'schema': {
                'type': 'object',
                'properties': {
                    'mensaje': {'type': 'string'},
                    'data': {'$ref': '#/definitions/Distancia'}
                }
            }
        },
        400: {
            'description': 'Error en el formato de datos'
        },
        404: {
            'description': 'Tag o anchor no encontrado'
        }
    }
})
def registrar_distancias():
    data = request.json
    
    # Verificar formato del JSON
    if not data.get('tag') or not data.get('anchors') or not isinstance(data.get('anchors'), list) or len(data.get('anchors')) != 3:
        return jsonify({"error": "Formato inválido. Se requiere un tag y exactamente 3 anchors"}), 400
    
    # Buscar el tag por su código
    tag = Tag.query.filter_by(codigo=data['tag']).first()
    if not tag:
        return jsonify({"error": f"El tag {data['tag']} no existe en la base de datos"}), 404
    
    # Buscar los anchors y guardar sus IDs
    anchors_data = []
    for i, anchor_data in enumerate(data['anchors']):
        if not anchor_data.get('shortAddres') or 'distancia' not in anchor_data:
            return jsonify({"error": f"Formato inválido para el anchor #{i+1}"}), 400
        
        # Buscar anchor por nombre
        anchor = Anchor.query.filter_by(nombre=anchor_data['shortAddres']).first()
        if not anchor:
            return jsonify({"error": f"El anchor {anchor_data['shortAddres']} no existe en la base de datos"}), 404
        
        # Convertir distancia a número
        try:
            distancia = float(anchor_data['distancia']) * 100  # Convertir a cm
        except ValueError:
            return jsonify({"error": f"La distancia debe ser un número válido para el anchor {anchor_data['shortAddres']}"}), 400
        
        anchors_data.append({
            'id': anchor.id,
            'distancia': distancia
        })
    
    # Verificar si ya existe una entrada de distancia para este tag
    distancia_existente = Distancia.query.filter_by(tag_id=tag.id).first()
    
    # Verificar cambios significativos en distancias (50 cm de diferencia)
    cambio_significativo = False
    if distancia_existente:
        distancias_anteriores = [
            distancia_existente.anchor1_dist if distancia_existente.anchor1_dist else 0,
            distancia_existente.anchor2_dist if distancia_existente.anchor2_dist else 0,
            distancia_existente.anchor3_dist if distancia_existente.anchor3_dist else 0
        ]
        
        for i, anchor_data in enumerate(anchors_data):
            if i < len(distancias_anteriores) and abs(anchor_data['distancia'] - distancias_anteriores[i]) >= 50.0:
                cambio_significativo = True
                break
    else:
        cambio_significativo = True  # Si no hay entrada previa, siempre es un cambio significativo
    
    # Actualizar o crear la entrada de distancias
    if distancia_existente:
        # Actualizar solo si hay cambios significativos
        if cambio_significativo:
            distancia_existente.anchor1_id = anchors_data[0]['id']
            distancia_existente.anchor1_dist = anchors_data[0]['distancia']
            distancia_existente.anchor2_id = anchors_data[1]['id']
            distancia_existente.anchor2_dist = anchors_data[1]['distancia']
            distancia_existente.anchor3_id = anchors_data[2]['id']
            distancia_existente.anchor3_dist = anchors_data[2]['distancia']
            db.session.commit()
            
            #Triangular posición después de actualizar distancias
            triangular_posicion(
                tag.id,
                distancia_existente.anchor1_id, distancia_existente.anchor1_dist,
                distancia_existente.anchor2_id, distancia_existente.anchor2_dist,
                distancia_existente.anchor3_id, distancia_existente.anchor3_dist
            )
            
            return jsonify({
                "mensaje": "Distancias actualizadas correctamente",
                "data": distancia_existente.to_dict()
            })
        else:
            return jsonify({
                "mensaje": "No hay cambios significativos en las distancias",
                "data": distancia_existente.to_dict()
            })
    else:
        # Crear nueva entrada
        nueva_distancia = Distancia(
            tag_id=tag.id,
            anchor1_id=anchors_data[0]['id'],
            anchor1_dist=anchors_data[0]['distancia'],
            anchor2_id=anchors_data[1]['id'],
            anchor2_dist=anchors_data[1]['distancia'],
            anchor3_id=anchors_data[2]['id'],
            anchor3_dist=anchors_data[2]['distancia']
        )
        
        db.session.add(nueva_distancia)
        db.session.commit()
        
        #Triangular posición después de crear nueva distancia
        triangular_posicion(
            tag.id,
            nueva_distancia.anchor1_id, nueva_distancia.anchor1_dist,
            nueva_distancia.anchor2_id, nueva_distancia.anchor2_dist,
            nueva_distancia.anchor3_id, nueva_distancia.anchor3_dist
        )
        
        # También actualizamos la última comunicación del tag
        tag.ultima_comunicacion = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "mensaje": "Distancias registradas correctamente",
            "data": nueva_distancia.to_dict()
        }), 201