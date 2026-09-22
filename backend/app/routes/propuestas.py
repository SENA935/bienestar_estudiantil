from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.propuesta import Propuesta
from ..models.alerta import Alerta
from ..models.auditoria import Auditoria
from ..extensions import db

propuestas_bp = Blueprint('propuestas', __name__)


@propuestas_bp.route('', methods=['GET'])
@jwt_required()
def get_propuestas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    estado = request.args.get('estado', '')
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)

    query = Propuesta.query
    if estado:
        query = query.filter_by(estado=estado)
    if user and user.rol and user.rol.nombre == 'Estudiante':
        query = query.filter_by(estudiante_id=user_id)

    pagination = query.order_by(Propuesta.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'success': True,
        'data': {
            'propuestas': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })


@propuestas_bp.route('', methods=['POST'])
@jwt_required()
def create_propuesta():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('titulo') or not data.get('descripcion'):
        return jsonify({'success': False, 'message': 'Título y descripción son requeridos'}), 400

    prop = Propuesta(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        estudiante_id=user_id,
        estado='Pendiente'
    )
    db.session.add(prop)

    coordinadores = Usuario.query.join(Usuario.rol).filter(
        Usuario.rol.has(nombre='Coordinador')
    ).all()
    for coord in coordinadores:
        alerta = Alerta(
            titulo='Nueva propuesta recibida',
            descripcion=f'Se ha recibido una nueva propuesta: {prop.titulo}',
            tipo='Propuesta recibida',
            usuario_id=coord.id
        )
        db.session.add(alerta)

    aud = Auditoria(usuario_id=user_id, modulo='Propuestas', accion='CREAR',
                    descripcion=f'Propuesta creada: {prop.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Propuesta creada correctamente', 'data': prop.to_dict()}), 201


@propuestas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_propuesta(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    prop = Propuesta.query.get_or_404(id)
    data = request.get_json()

    prop.estado = data.get('estado', prop.estado)
    prop.observaciones_coordinador = data.get('observaciones_coordinador', prop.observaciones_coordinador)

    alerta = Alerta(
        titulo=f'Propuesta {prop.estado.lower()}',
        descripcion=f'Tu propuesta "{prop.titulo}" ha sido {prop.estado.lower()}.',
        tipo='Propuesta recibida',
        usuario_id=prop.estudiante_id
    )
    db.session.add(alerta)

    aud = Auditoria(usuario_id=user_id, modulo='Propuestas', accion='ACTUALIZAR',
                    descripcion=f'Propuesta #{prop.id} actualizada a {prop.estado}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Propuesta actualizada correctamente', 'data': prop.to_dict()})
