from flask import Blueprint, request, jsonify
from extensions import db
from models.taller import Taller
from models.zona import Zona
from models.anchor import Anchor
from sqlalchemy import func

# Crear el blueprint para los talleres
taller_bp = Blueprint('talleres', __name__, url_prefix='/api/talleres')

# Obtener todos los talleres
@taller_bp.route('/', methods=['GET'])
def get_all_talleres():
    talleres = Taller.query.all()
    return jsonify([taller.to_dict() for taller in talleres])

# Obtener un taller específico
@taller_bp.route('/<int:id>', methods=['GET'])
def get_taller(id):
    taller = Taller.query.get_or_404(id)
    return jsonify(taller.to_dict())

# Crear un nuevo taller
@taller_bp.route('/', methods=['POST'])
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
def get_taller_zonas(id):
    # Verificar que el taller existe
    Taller.query.get_or_404(id)
    
    zonas = Zona.query.filter_by(taller_id=id).all()
    return jsonify([zona.to_dict() for zona in zonas])

# Obtener todos los anchors de un taller
@taller_bp.route('/<int:id>/anchors', methods=['GET'])
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