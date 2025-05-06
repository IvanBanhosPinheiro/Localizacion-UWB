from flask import Blueprint, request, jsonify
from extensions import db
from models.alerta import Alerta
from models.tag import Tag
from models.vehiculo import Vehiculo

# Crear el blueprint para las alertas
alerta_bp = Blueprint('alertas', __name__, url_prefix='/api/alertas')

# Obtener todas las alertas
@alerta_bp.route('/', methods=['GET'])
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
def get_alerta(id):
    alerta = Alerta.query.get_or_404(id)
    return jsonify(alerta.to_dict())

# Crear una nueva alerta
@alerta_bp.route('/', methods=['POST'])
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
def delete_alerta(id):
    alerta = Alerta.query.get_or_404(id)
    db.session.delete(alerta)
    db.session.commit()
    
    return '', 204

# Marcar una alerta como leída
@alerta_bp.route('/<int:id>/marcar-leida', methods=['PUT'])
def marcar_leida(id):
    alerta = Alerta.query.get_or_404(id)
    alerta.leido = True
    db.session.commit()
    
    return jsonify(alerta.to_dict())

# Obtener alertas no leídas
@alerta_bp.route('/no-leidas', methods=['GET'])
def get_no_leidas():
    alertas_no_leidas = Alerta.query.filter_by(leido=False).all()
    return jsonify([alerta.to_dict() for alerta in alertas_no_leidas])