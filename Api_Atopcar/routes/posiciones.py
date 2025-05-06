from flask import Blueprint, request, jsonify
from extensions import db
from models.posicion import Posicion
from models.tag import Tag
from models.zona import Zona
from sqlalchemy import desc
from datetime import datetime, timedelta

# Crear el blueprint para las posiciones
posicion_bp = Blueprint('posiciones', __name__, url_prefix='/api/posiciones')

# Obtener todas las posiciones
@posicion_bp.route('/', methods=['GET'])
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
def get_posicion(id):
    posicion = Posicion.query.get_or_404(id)
    return jsonify(posicion.to_dict())

# Crear una nueva posición
@posicion_bp.route('/', methods=['POST'])
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
def delete_posicion(id):
    posicion = Posicion.query.get_or_404(id)
    db.session.delete(posicion)
    db.session.commit()
    
    return '', 204

# Obtener la última posición de un tag específico
@posicion_bp.route('/tag/<int:tag_id>/ultima', methods=['GET'])
def get_ultima_posicion(tag_id):
    # Verificar que el tag existe
    if not Tag.query.get(tag_id):
        return jsonify({"error": "El tag especificado no existe"}), 404
    
    ultima_posicion = Posicion.query.filter_by(tag_id=tag_id).order_by(desc(Posicion.timestamp)).first()
    
    if not ultima_posicion:
        return jsonify({"error": "No hay posiciones registradas para este tag"}), 404
    
    return jsonify(ultima_posicion.to_dict())