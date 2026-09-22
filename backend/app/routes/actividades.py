from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.actividad import Actividad
from ..models.auditoria import Auditoria
from ..extensions import db

actividades_bp = Blueprint('actividades', __name__)


@actividades_bp.route('', methods=['GET'])
@jwt_required()
def get_actividades():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    estado = request.args.get('estado', '')

    query = Actividad.query
    if search:
        query = query.filter(Actividad.titulo.ilike(f'%{search}%'))
    if categoria:
        query = query.filter_by(categoria=categoria)
    if estado:
        query = query.filter_by(estado=estado)

    pagination = query.order_by(Actividad.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'success': True,
        'data': {
            'actividades': [a.to_dict() for a in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })


@actividades_bp.route('', methods=['POST'])
@jwt_required()
def create_actividad():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('titulo') or not data.get('categoria'):
        return jsonify({'success': False, 'message': 'Título y categoría son requeridos'}), 400

    act = Actividad(
        titulo=data['titulo'], descripcion=data.get('descripcion'),
        categoria=data['categoria'], duracion=data.get('duracion', 30),
        instrucciones=data.get('instrucciones'),
        estado=data.get('estado', 'Activa')
    )
    db.session.add(act)
    aud = Auditoria(usuario_id=user_id, modulo='Actividades', accion='CREAR',
                    descripcion=f'Actividad creada: {act.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad creada correctamente', 'data': act.to_dict()}), 201


@actividades_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_actividad(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    act = Actividad.query.get_or_404(id)
    data = request.get_json()

    act.titulo = data.get('titulo', act.titulo)
    act.descripcion = data.get('descripcion', act.descripcion)
    act.categoria = data.get('categoria', act.categoria)
    act.duracion = data.get('duracion', act.duracion)
    act.instrucciones = data.get('instrucciones', act.instrucciones)
    act.estado = data.get('estado', act.estado)

    aud = Auditoria(usuario_id=user_id, modulo='Actividades', accion='ACTUALIZAR',
                    descripcion=f'Actividad actualizada: {act.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad actualizada correctamente', 'data': act.to_dict()})


@actividades_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_actividad(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    act = Actividad.query.get_or_404(id)
    aud = Auditoria(usuario_id=user_id, modulo='Actividades', accion='ELIMINAR',
                    descripcion=f'Actividad eliminada: {act.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.delete(act)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad eliminada correctamente'})


@actividades_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_actividades():
    acts = Actividad.query.filter_by(estado='Activa').all()
    return jsonify({'success': True, 'data': [a.to_dict() for a in acts]})
