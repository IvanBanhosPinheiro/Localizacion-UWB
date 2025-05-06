from flask import Blueprint, request, jsonify
from extensions import db
from models.zona import Zona
from models.taller import Taller
from models.anchor import Anchor
from models.posicion import Posicion

# Crear el blueprint para las zonas
zona_bp = Blueprint('zonas', __name__, url_prefix='/api/zonas')

# Obtener todas las zonas
@zona_bp.route('/', methods=['GET'])
def get_all_zonas():
    # Filtrar por taller_id si se especifica
    taller_id = request.args.get('taller_id', type=int)
    # Filtrar por tipo de zona
    tipo = request.args.get('tipo')
    
    query = Zona.query
    
    if taller_id:
        query = query.filter_by(taller_id=taller_id)
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    zonas = query.all()
    return jsonify([zona.to_dict() for zona in zonas])

# Obtener una zona específica
@zona_bp.route('/<int:id>', methods=['GET'])
def get_zona(id):
    zona = Zona.query.get_or_404(id)
    return jsonify(zona.to_dict())

# Crear una nueva zona
@zona_bp.route('/', methods=['POST'])
def create_zona():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('nombre'):
        return jsonify({"error": "El nombre de la zona es obligatorio"}), 400
    
    # Verificar que el taller existe
    if data.get('taller_id') and not Taller.query.get(data['taller_id']):
        return jsonify({"error": "El taller especificado no existe"}), 400
    
    nueva_zona = Zona(
        nombre=data['nombre'],
        tipo=data.get('tipo'),
        color_hex=data.get('color_hex'),
        taller_id=data.get('taller_id')
    )
    
    db.session.add(nueva_zona)
    db.session.commit()
    
    return jsonify(nueva_zona.to_dict()), 201

# Actualizar una zona
@zona_bp.route('/<int:id>', methods=['PUT'])
def update_zona(id):
    zona = Zona.query.get_or_404(id)
    data = request.json
    
    # Verificar que el taller existe si se cambia
    if 'taller_id' in data and data['taller_id'] and not Taller.query.get(data['taller_id']):
        return jsonify({"error": "El taller especificado no existe"}), 400
    
    # Actualizar campos
    if 'nombre' in data:
        zona.nombre = data['nombre']
    if 'tipo' in data:
        zona.tipo = data['tipo']
    if 'color_hex' in data:
        zona.color_hex = data['color_hex']
    if 'taller_id' in data:
        zona.taller_id = data['taller_id']
    
    db.session.commit()
    
    return jsonify(zona.to_dict())

# Eliminar una zona
@zona_bp.route('/<int:id>', methods=['DELETE'])
def delete_zona(id):
    zona = Zona.query.get_or_404(id)
    
    # Verificar si hay anchors en la zona
    anchors_count = Anchor.query.filter_by(zona_id=id).count()
    if anchors_count > 0:
        return jsonify({"error": f"No se puede eliminar la zona porque tiene {anchors_count} anchors asociados"}), 400
    
    # Verificar si hay posiciones registradas en la zona
    posiciones_count = Posicion.query.filter_by(zona_id=id).count()
    if posiciones_count > 0:
        return jsonify({"error": f"No se puede eliminar la zona porque tiene {posiciones_count} posiciones registradas"}), 400
    
    db.session.delete(zona)
    db.session.commit()
    
    return '', 204

# Obtener todos los anchors de una zona
@zona_bp.route('/<int:id>/anchors', methods=['GET'])
def get_zona_anchors(id):
    # Verificar que la zona existe
    Zona.query.get_or_404(id)
    
    # Filtrar anchors activos si se especifica
    activo = request.args.get('activo')
    
    query = Anchor.query.filter_by(zona_id=id)
    
    if activo is not None:
        activo_bool = activo.lower() == 'true'
        query = query.filter_by(activo=activo_bool)
    
    anchors = query.all()
    return jsonify([anchor.to_dict() for anchor in anchors])

# Obtener estadísticas de la zona
@zona_bp.route('/<int:id>/stats', methods=['GET'])
def get_zona_stats(id):
    zona = Zona.query.get_or_404(id)
    
    num_anchors = Anchor.query.filter_by(zona_id=id).count()
    num_anchors_activos = Anchor.query.filter_by(zona_id=id, activo=True).count()
    
    # Contar posiciones en las últimas 24 horas
    from datetime import datetime, timedelta
    limite_tiempo = datetime.utcnow() - timedelta(hours=24)
    posiciones_recientes = Posicion.query.filter_by(zona_id=id).filter(Posicion.timestamp >= limite_tiempo).count()
    
    return jsonify({
        'id': id,
        'nombre': zona.nombre,
        'tipo': zona.tipo,
        'taller_id': zona.taller_id,
        'anchors': {
            'total': num_anchors,
            'activos': num_anchors_activos,
            'inactivos': num_anchors - num_anchors_activos
        },
        'posiciones_24h': posiciones_recientes
    })