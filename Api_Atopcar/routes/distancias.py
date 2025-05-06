from flask import Blueprint, request, jsonify
from extensions import db
from models.distancia import Distancia
from models.tag import Tag
from models.anchor import Anchor
from datetime import datetime

# Crear el blueprint para las distancias
distancia_bp = Blueprint('distancias', __name__, url_prefix='/api/distancias')

# Obtener todas las distancias
@distancia_bp.route('/', methods=['GET'])
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
def get_distancia(id):
    distancia = Distancia.query.get_or_404(id)
    return jsonify(distancia.to_dict())

# Crear una nueva distancia
@distancia_bp.route('/', methods=['POST'])
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
    
    return jsonify(nueva_distancia.to_dict()), 201

# Actualizar una distancia
@distancia_bp.route('/<int:id>', methods=['PUT'])
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
    
    return jsonify(distancia.to_dict())

# Eliminar una distancia
@distancia_bp.route('/<int:id>', methods=['DELETE'])
def delete_distancia(id):
    distancia = Distancia.query.get_or_404(id)
    db.session.delete(distancia)
    db.session.commit()
    
    return '', 204

# Obtener la última distancia para un tag específico
@distancia_bp.route('/tag/<int:tag_id>', methods=['GET'])
def get_by_tag(tag_id):
    distancia = Distancia.query.filter_by(tag_id=tag_id).first_or_404()
    return jsonify(distancia.to_dict())



# Registrar distancias desde un dispositivo
@distancia_bp.route('/registrar', methods=['POST'])
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
            distancia = float(anchor_data['distancia'])
        except ValueError:
            return jsonify({"error": f"La distancia debe ser un número válido para el anchor {anchor_data['shortAddres']}"}), 400
        
        anchors_data.append({
            'id': anchor.id,
            'distancia': distancia
        })
    
    # Verificar si ya existe una entrada de distancia para este tag
    distancia_existente = Distancia.query.filter_by(tag_id=tag.id).first()
    
    # Verificar cambios significativos en distancias (1m de diferencia)
    cambio_significativo = False
    if distancia_existente:
        distancias_anteriores = [
            distancia_existente.anchor1_dist if distancia_existente.anchor1_dist else 0,
            distancia_existente.anchor2_dist if distancia_existente.anchor2_dist else 0,
            distancia_existente.anchor3_dist if distancia_existente.anchor3_dist else 0
        ]
        
        for i, anchor_data in enumerate(anchors_data):
            if i < len(distancias_anteriores) and abs(anchor_data['distancia'] - distancias_anteriores[i]) >= 1.0:
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
        
        # También actualizamos la última comunicación del tag
        tag.ultima_comunicacion = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "mensaje": "Distancias registradas correctamente",
            "data": nueva_distancia.to_dict()
        }), 201