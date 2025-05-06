from flask import Blueprint, request, jsonify
from extensions import db
from models.tag import Tag
from models.vehiculo import Vehiculo
from datetime import datetime

# Crear el blueprint para los tags
tag_bp = Blueprint('tags', __name__, url_prefix='/api/tags')

# Obtener todos los tags
@tag_bp.route('/', methods=['GET'])
def get_all_tags():
    # Filtrar por estado si se especifica
    estado = request.args.get('estado')
    # Filtrar por batería baja
    bateria_baja = request.args.get('bateria_baja')
    # Filtrar tags asignados o no asignados
    asignado = request.args.get('asignado')
    
    query = Tag.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    if bateria_baja is not None:
        if bateria_baja.lower() == 'true':
            query = query.filter(Tag.bateria < 20)  # Considerar baja a menos del 20%
    
    tags = query.all()
    
    if asignado is not None:
        asignado_bool = asignado.lower() == 'true'
        # Filtrar en memoria ya que necesitamos acceder a la relación
        if asignado_bool:
            tags = [tag for tag in tags if tag.vehiculo is not None]
        else:
            tags = [tag for tag in tags if tag.vehiculo is None]
    
    return jsonify([tag.to_dict() for tag in tags])

# Obtener un tag específico
@tag_bp.route('/<int:id>', methods=['GET'])
def get_tag(id):
    tag = Tag.query.get_or_404(id)
    return jsonify(tag.to_dict())

# Crear un nuevo tag
@tag_bp.route('/', methods=['POST'])
def create_tag():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('codigo') or not data.get('mac'):
        return jsonify({"error": "El código y la MAC son obligatorios"}), 400
    
    # Verificar que el código y la MAC sean únicos
    if Tag.query.filter_by(codigo=data['codigo']).first():
        return jsonify({"error": f"Ya existe un tag con el código {data['codigo']}"}), 400
    
    if Tag.query.filter_by(mac=data['mac']).first():
        return jsonify({"error": f"Ya existe un tag con la MAC {data['mac']}"}), 400
    
    nuevo_tag = Tag(
        codigo=data['codigo'],
        mac=data['mac'],
        estado=data.get('estado', 'libre'),
        bateria=data.get('bateria'),
        ultima_comunicacion=datetime.utcnow(),
        observaciones=data.get('observaciones')
    )
    
    db.session.add(nuevo_tag)
    db.session.commit()
    
    return jsonify(nuevo_tag.to_dict()), 201

# Actualizar un tag
@tag_bp.route('/<int:id>', methods=['PUT'])
def update_tag(id):
    tag = Tag.query.get_or_404(id)
    data = request.json
    
    # Verificar que el código sea único si se cambia
    if 'codigo' in data and data['codigo'] != tag.codigo:
        if Tag.query.filter_by(codigo=data['codigo']).first():
            return jsonify({"error": f"Ya existe un tag con el código {data['codigo']}"}), 400
    
    # Verificar que la MAC sea única si se cambia
    if 'mac' in data and data['mac'] != tag.mac:
        if Tag.query.filter_by(mac=data['mac']).first():
            return jsonify({"error": f"Ya existe un tag con la MAC {data['mac']}"}), 400
    
    # Actualizar campos
    if 'codigo' in data:
        tag.codigo = data['codigo']
    if 'mac' in data:
        tag.mac = data['mac']
    if 'estado' in data:
        tag.estado = data['estado']
    if 'bateria' in data:
        tag.bateria = data['bateria']
    if 'observaciones' in data:
        tag.observaciones = data['observaciones']
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Eliminar un tag
@tag_bp.route('/<int:id>', methods=['DELETE'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    # Verificar si el tag está asignado a un vehículo
    if tag.vehiculo:
        return jsonify({"error": "No se puede eliminar un tag asignado a un vehículo. Desasigne primero el tag."}), 400
    
    db.session.delete(tag)
    db.session.commit()
    
    return '', 204

# Asignar un tag a un vehículo
@tag_bp.route('/<int:id>/asignar/<int:vehiculo_id>', methods=['PUT'])
def asignar_vehiculo(id, vehiculo_id):
    tag = Tag.query.get_or_404(id)
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    
    # Verificar que el tag no esté ya asignado
    if tag.vehiculo:
        return jsonify({"error": f"El tag ya está asignado al vehículo {tag.vehiculo.id}"}), 400
    
    # Verificar que el vehículo no tenga ya un tag asignado
    if Vehiculo.query.filter(Vehiculo.tag != None).filter_by(id=vehiculo_id).first():
        return jsonify({"error": "El vehículo ya tiene un tag asignado"}), 400
    
    # Asignar el tag al vehículo
    vehiculo.tag = tag
    tag.estado = 'asignado'
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Desasignar un tag de un vehículo
@tag_bp.route('/<int:id>/desasignar', methods=['PUT'])
def desasignar_vehiculo(id):
    tag = Tag.query.get_or_404(id)
    
    # Verificar que el tag esté asignado
    if not tag.vehiculo:
        return jsonify({"error": "El tag no está asignado a ningún vehículo"}), 400
    
    # Desasignar el tag
    tag.vehiculo = None
    tag.estado = 'libre'
    
    db.session.commit()
    
    return jsonify(tag.to_dict())

# Actualizar el nivel de batería de un tag
@tag_bp.route('/<int:id>/bateria', methods=['PUT'])
def update_bateria(id):
    tag = Tag.query.get_or_404(id)
    data = request.json
    
    if 'bateria' not in data:
        return jsonify({"error": "No se ha especificado el nivel de batería"}), 400
    
    tag.bateria = data['bateria']
    tag.ultima_comunicacion = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(tag.to_dict())