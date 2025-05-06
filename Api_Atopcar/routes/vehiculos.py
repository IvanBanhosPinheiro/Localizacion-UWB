from flask import Blueprint, request, jsonify
from extensions import db
from models.vehiculo import Vehiculo
from models.tag import Tag

# Crear el blueprint para los vehículos
vehiculo_bp = Blueprint('vehiculos', __name__, url_prefix='/api/vehiculos')

# Obtener todos los vehículos
@vehiculo_bp.route('/', methods=['GET'])
def get_all_vehiculos():
    # Filtrar por estado si se especifica
    estado = request.args.get('estado')
    # Filtrar vehículos con/sin tag
    con_tag = request.args.get('con_tag')
    
    query = Vehiculo.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    vehiculos = query.all()
    
    # Filtrar por vehículos con tag o sin tag
    if con_tag is not None:
        con_tag_bool = con_tag.lower() == 'true'
        if con_tag_bool:
            vehiculos = [v for v in vehiculos if hasattr(v, 'tag') and v.tag]
        else:
            vehiculos = [v for v in vehiculos if not hasattr(v, 'tag') or not v.tag]
    
    return jsonify([vehiculo.to_dict() for vehiculo in vehiculos])

# Obtener un vehículo específico
@vehiculo_bp.route('/<int:id>', methods=['GET'])
def get_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    return jsonify(vehiculo.to_dict())

# Crear un nuevo vehículo
@vehiculo_bp.route('/', methods=['POST'])
def create_vehiculo():
    data = request.json
    
    # Verificar campos obligatorios
    if not data.get('matricula') and not data.get('bastidor'):
        return jsonify({"error": "Se requiere al menos matrícula o bastidor"}), 400
    
    # Verificar que el bastidor sea único si se proporciona
    if data.get('bastidor') and Vehiculo.query.filter_by(bastidor=data['bastidor']).first():
        return jsonify({"error": f"Ya existe un vehículo con el bastidor {data['bastidor']}"}), 400
    
    nuevo_vehiculo = Vehiculo(
        matricula=data.get('matricula'),
        bastidor=data.get('bastidor'),
        referencia=data.get('referencia'),
        estado=data.get('estado', 'activo')
    )
    
    db.session.add(nuevo_vehiculo)
    db.session.commit()
    
    return jsonify(nuevo_vehiculo.to_dict()), 201

# Actualizar un vehículo
@vehiculo_bp.route('/<int:id>', methods=['PUT'])
def update_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    data = request.json
    
    # Verificar que el bastidor sea único si se cambia
    if 'bastidor' in data and data['bastidor'] != vehiculo.bastidor:
        if data['bastidor'] and Vehiculo.query.filter_by(bastidor=data['bastidor']).first():
            return jsonify({"error": f"Ya existe un vehículo con el bastidor {data['bastidor']}"}), 400
    
    # Actualizar campos
    if 'matricula' in data:
        vehiculo.matricula = data['matricula']
    if 'bastidor' in data:
        vehiculo.bastidor = data['bastidor']
    if 'referencia' in data:
        vehiculo.referencia = data['referencia']
    if 'estado' in data:
        vehiculo.estado = data['estado']
    
    db.session.commit()
    
    return jsonify(vehiculo.to_dict())

# Eliminar un vehículo
@vehiculo_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehiculo(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    
    # Verificar si el vehículo tiene un tag asignado
    if hasattr(vehiculo, 'tag') and vehiculo.tag:
        return jsonify({"error": "No se puede eliminar un vehículo con un tag asignado. Desasigne primero el tag."}), 400
    
    db.session.delete(vehiculo)
    db.session.commit()
    
    return '', 204

# Cambiar el estado de un vehículo
@vehiculo_bp.route('/<int:id>/estado', methods=['PUT'])
def cambiar_estado(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    data = request.json
    
    if not data.get('estado'):
        return jsonify({"error": "El estado es obligatorio"}), 400
    
    # Verificar que el estado sea válido
    if data['estado'] not in ['activo', 'entregado', 'baja']:
        return jsonify({"error": "Estado no válido. Debe ser 'activo', 'entregado' o 'baja'"}), 400
    
    vehiculo.estado = data['estado']
    db.session.commit()
    
    return jsonify(vehiculo.to_dict())

# Obtener el tag asociado a un vehículo
@vehiculo_bp.route('/<int:id>/tag', methods=['GET'])
def get_vehiculo_tag(id):
    vehiculo = Vehiculo.query.get_or_404(id)
    
    if not hasattr(vehiculo, 'tag') or not vehiculo.tag:
        return jsonify({"error": "El vehículo no tiene un tag asignado"}), 404
    
    return jsonify(vehiculo.tag.to_dict())

# Buscar vehículos por matrícula o bastidor
@vehiculo_bp.route('/buscar', methods=['GET'])
def buscar_vehiculo():
    termino = request.args.get('termino')
    
    if not termino:
        return jsonify({"error": "El término de búsqueda es obligatorio"}), 400
    
    # Buscar vehículos que coincidan con el término en matrícula o bastidor
    vehiculos = Vehiculo.query.filter(
        (Vehiculo.matricula.like(f"%{termino}%")) |
        (Vehiculo.bastidor.like(f"%{termino}%")) |
        (Vehiculo.referencia.like(f"%{termino}%"))
    ).all()
    
    return jsonify([vehiculo.to_dict() for vehiculo in vehiculos])