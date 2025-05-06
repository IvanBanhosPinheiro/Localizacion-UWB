from flask import Blueprint, request, jsonify
from extensions import db
from models.anchor import Anchor
from models.taller import Taller
from models.zona import Zona

# Crear el blueprint para los anchors
anchor_bp = Blueprint('anchors', __name__, url_prefix='/api/anchors')

# Obtener todos los anchors
@anchor_bp.route('/', methods=['GET'])
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
def get_anchor(id):
    anchor = Anchor.query.get_or_404(id)
    return jsonify(anchor.to_dict())

# Crear un nuevo anchor
@anchor_bp.route('/', methods=['POST'])
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
def delete_anchor(id):
    anchor = Anchor.query.get_or_404(id)
    db.session.delete(anchor)
    db.session.commit()
    
    return '', 204

# Activar/desactivar un anchor
@anchor_bp.route('/<int:id>/toggle-activo', methods=['PUT'])
def toggle_activo(id):
    anchor = Anchor.query.get_or_404(id)
    anchor.activo = not anchor.activo
    db.session.commit()
    
    return jsonify(anchor.to_dict())