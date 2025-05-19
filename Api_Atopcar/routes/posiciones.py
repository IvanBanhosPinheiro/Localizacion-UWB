from flask import Blueprint, request, jsonify
from extensions import db
from models.posicion import Posicion
from models.tag import Tag
from models.zona import Zona
from sqlalchemy import desc
from datetime import datetime, timedelta
from models.anchor import Anchor
import numpy as np
import traceback
from flasgger import swag_from

# Crear el blueprint para las posiciones
posicion_bp = Blueprint('posiciones', __name__, url_prefix='/api/posiciones')

# Obtener todas las posiciones
@posicion_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Obtener todas las posiciones',
    'description': 'Recupera la lista de posiciones registradas con opciones de filtrado',
    'parameters': [
        {
            'name': 'tag_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por ID del tag'
        },
        {
            'name': 'zona_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por ID de la zona'
        },
        {
            'name': 'hours',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrar por últimas N horas'
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 100,
            'description': 'Límite de resultados a devolver'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de posiciones',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Posicion'}
            }
        }
    }
})
def get_all_posiciones():
    # Filtrar por tag_id
    tag_id = request.args.get('tag_id', type=int)
    # Filtrar por zona_id
    zona_id = request.args.get('zona_id', type=int)
    # Filtrar por fecha (últimas N horas)
    hours = request.args.get('hours', type=int)
    # Limitar número de resultados
    limit = request.args.get('limit', type=int, default=100)
    
    query = Posicion.query
    
    if tag_id:
        query = query.filter_by(tag_id=tag_id)
    if zona_id:
        query = query.filter_by(zona_id=zona_id)
    if hours:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Posicion.timestamp >= time_threshold)
    
    # Ordenar por timestamp descendente (más recientes primero)
    query = query.order_by(desc(Posicion.timestamp)).limit(limit)
    
    posiciones = query.all()
    return jsonify([posicion.to_dict() for posicion in posiciones])

# Obtener una posición específica
@posicion_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Obtener una posición específica',
    'description': 'Recupera los detalles de una posición por su ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la posición'
        }
    ],
    'responses': {
        200: {
            'description': 'Detalles de la posición',
            'schema': {'$ref': '#/definitions/Posicion'}
        },
        404: {
            'description': 'Posición no encontrada'
        }
    }
})
def get_posicion(id):
    posicion = Posicion.query.get_or_404(id)
    return jsonify(posicion.to_dict())

# Crear una nueva posición
@posicion_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Crear una nueva posición',
    'description': 'Registra una nueva posición para un tag',
    'parameters': [
        {
            'name': 'posicion',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag UWB'},
                    'x': {'type': 'integer', 'description': 'Coordenada X en el plano del taller (cm)'},
                    'y': {'type': 'integer', 'description': 'Coordenada Y en el plano del taller (cm)'},
                    'zona_id': {'type': 'integer', 'description': 'ID de la zona donde se encuentra el tag'}
                },
                'required': ['tag_id', 'x', 'y']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Posición creada exitosamente',
            'schema': {'$ref': '#/definitions/Posicion'}
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def create_posicion():
    data = request.json
    
    # Verificar que el tag existe
    tag_id = data.get('tag_id')
    if tag_id and not Tag.query.get(tag_id):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    # Verificar que la zona existe
    zona_id = data.get('zona_id')
    if zona_id and not Zona.query.get(zona_id):
        return jsonify({"error": "La zona especificada no existe"}), 400
    
    # Verificar que se proporcionan las coordenadas
    if 'x' not in data or 'y' not in data:
        return jsonify({"error": "Las coordenadas x e y son obligatorias"}), 400
    
    nueva_posicion = Posicion(
        tag_id=tag_id,
        x=data['x'],
        y=data['y'],
        zona_id=zona_id
    )
    
    db.session.add(nueva_posicion)
    db.session.commit()
    
    return jsonify(nueva_posicion.to_dict()), 201

# Actualizar una posición
@posicion_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Actualizar una posición',
    'description': 'Modifica los datos de una posición existente',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la posición a modificar'
        },
        {
            'name': 'posicion',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tag_id': {'type': 'integer', 'description': 'ID del tag UWB'},
                    'x': {'type': 'integer', 'description': 'Coordenada X en el plano del taller (cm)'},
                    'y': {'type': 'integer', 'description': 'Coordenada Y en el plano del taller (cm)'},
                    'zona_id': {'type': 'integer', 'description': 'ID de la zona donde se encuentra el tag'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Posición actualizada correctamente',
            'schema': {'$ref': '#/definitions/Posicion'}
        },
        404: {
            'description': 'Posición no encontrada'
        },
        400: {
            'description': 'Error en los datos enviados'
        }
    }
})
def update_posicion(id):
    posicion = Posicion.query.get_or_404(id)
    data = request.json
    
    # Verificar que el tag existe si se actualiza
    if 'tag_id' in data and data['tag_id'] and not Tag.query.get(data['tag_id']):
        return jsonify({"error": "El tag especificado no existe"}), 400
    
    # Verificar que la zona existe si se actualiza
    if 'zona_id' in data and data['zona_id'] and not Zona.query.get(data['zona_id']):
        return jsonify({"error": "La zona especificada no existe"}), 400
    
    # Actualizar campos
    if 'tag_id' in data:
        posicion.tag_id = data['tag_id']
    if 'x' in data:
        posicion.x = data['x']
    if 'y' in data:
        posicion.y = data['y']
    if 'zona_id' in data:
        posicion.zona_id = data['zona_id']
    
    db.session.commit()
    
    return jsonify(posicion.to_dict())

# Eliminar una posición
@posicion_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Eliminar una posición',
    'description': 'Elimina permanentemente una posición del sistema',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la posición a eliminar'
        }
    ],
    'responses': {
        204: {
            'description': 'Posición eliminada correctamente (sin contenido)'
        },
        404: {
            'description': 'Posición no encontrada'
        }
    }
})
def delete_posicion(id):
    posicion = Posicion.query.get_or_404(id)
    db.session.delete(posicion)
    db.session.commit()
    
    return '', 204

# Obtener la última posición de un tag específico
@posicion_bp.route('/tag/<int:tag_id>/ultima', methods=['GET'])
@swag_from({
    'tags': ['posiciones'],
    'summary': 'Obtener última posición de un tag',
    'description': 'Recupera la posición más reciente registrada para un tag específico',
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
            'description': 'Última posición del tag',
            'schema': {'$ref': '#/definitions/Posicion'}
        },
        404: {
            'description': 'Tag no encontrado o sin posiciones registradas'
        }
    }
})
def get_ultima_posicion(tag_id):
    # Verificar que el tag existe
    if not Tag.query.get(tag_id):
        return jsonify({"error": "El tag especificado no existe"}), 404
    
    ultima_posicion = Posicion.query.filter_by(tag_id=tag_id).order_by(desc(Posicion.timestamp)).first()
    
    if not ultima_posicion:
        return jsonify({"error": "No hay posiciones registradas para este tag"}), 404
    
    return jsonify(ultima_posicion.to_dict())



# Función de triangulación (se puede llamar desde el módulo de distancias)
def triangular_posicion(tag_id, anchor1_id, anchor1_dist, anchor2_id, anchor2_dist, anchor3_id, anchor3_dist):
    try:
        # Obtener las coordenadas de los anchors
        anchor1 = Anchor.query.get(anchor1_id)
        anchor2 = Anchor.query.get(anchor2_id)
        anchor3 = Anchor.query.get(anchor3_id)
        
        if not (anchor1 and anchor2 and anchor3):
            print(f"Error: No se encontraron todos los anchors ({anchor1_id}, {anchor2_id}, {anchor3_id})")
            return None
            
        # Verificar que todas las coordenadas son válidas
        if None in (anchor1.x, anchor1.y, anchor2.x, anchor2.y, anchor3.x, anchor3.y):
            print("Error: Coordenadas de anchors nulas")
            return None
            
        print(f"Anchor1 ({anchor1.nombre}): ({anchor1.x}, {anchor1.y}) dist: {anchor1_dist}")
        print(f"Anchor2 ({anchor2.nombre}): ({anchor2.x}, {anchor2.y}) dist: {anchor2_dist}")
        print(f"Anchor3 ({anchor3.nombre}): ({anchor3.x}, {anchor3.y}) dist: {anchor3_dist}")
        
        # Método basado en solución de ecuaciones lineales
        # Ecuaciones para trilateración: 
        # (x-x1)² + (y-y1)² = r1²
        # (x-x2)² + (y-y2)² = r2²
        # (x-x3)² + (y-y3)² = r3²
        
        # Restamos primera ecuación de las otras y resolvemos sistema lineal
        A = np.array([
            [2*(anchor2.x-anchor1.x), 2*(anchor2.y-anchor1.y)],
            [2*(anchor3.x-anchor1.x), 2*(anchor3.y-anchor1.y)]
        ])
        
        b = np.array([
            pow(anchor1_dist, 2) - pow(anchor2_dist, 2) - pow(anchor1.x, 2) + pow(anchor2.x, 2) - pow(anchor1.y, 2) + pow(anchor2.y, 2),
            pow(anchor1_dist, 2) - pow(anchor3_dist, 2) - pow(anchor1.x, 2) + pow(anchor3.x, 2) - pow(anchor1.y, 2) + pow(anchor3.y, 2)
        ])
        
        try:
            # Resolver sistema de ecuaciones
            position = np.linalg.solve(A, b)
            x, y = position[0], position[1]
            
            print(f"Posición calculada: ({x:.2f}, {y:.2f})")
            
            # Redondear a enteros para guardar en la base de datos
            x_int, y_int = int(round(x)), int(round(y))
            
            # Determinar zona (simplemente usamos la zona del anchor más cercano)
            zona_id = anchor1.zona_id
            
            # Crear nueva posición
            nueva_posicion = Posicion(
                tag_id=tag_id,
                x=x_int,
                y=y_int,
                zona_id=zona_id
            )
            
            db.session.add(nueva_posicion)
            db.session.commit()
            
            return nueva_posicion
            
        except np.linalg.LinAlgError:
            # Si el sistema no tiene solución única, usar método alternativo
            print("No se pudo resolver el sistema de ecuaciones. Usando método alternativo...")
            # Implementar método de minimización de errores aquí
            
            # Método simple: posición promedio ponderada por inverso de distancias
            total_weight = 1/anchor1_dist + 1/anchor2_dist + 1/anchor3_dist
            x = (anchor1.x/anchor1_dist + anchor2.x/anchor2_dist + anchor3.x/anchor3_dist) / total_weight
            y = (anchor1.y/anchor1_dist + anchor2.y/anchor2_dist + anchor3.y/anchor3_dist) / total_weight
            
            x_int, y_int = int(round(x)), int(round(y))
            
            zona_id = anchor1.zona_id
            
            nueva_posicion = Posicion(
                tag_id=tag_id,
                x=x_int,
                y=y_int,
                zona_id=zona_id
            )
            
            db.session.add(nueva_posicion)
            db.session.commit()
            
            return nueva_posicion
            
    except Exception as e:
        print(f"Error en triangulación: {str(e)}")
        traceback.print_exc()  # Imprime el traceback completo
        db.session.rollback()
        return None