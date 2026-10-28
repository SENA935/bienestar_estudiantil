from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.alerta import Alerta
from ..models.usuario import Usuario
from ..extensions import db

alertas_bp = Blueprint('alertas', __name__)


@alertas_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    rol = u.rol.nombre if u else ''
    if rol in ['Administrador', 'Coordinador']:
        alertas = Alerta.query.filter(
            (Alerta.usuario_id == uid) | (Alerta.destinatario == 'Todos') |
            (Alerta.destinatario == 'Profesores') | (Alerta.destinatario == 'Estudiantes')
        ).order_by(Alerta.fecha_creacion.desc()).all()
    elif rol in ['Profesor', 'Director de grupo']:
        alertas = Alerta.query.filter(
            (Alerta.usuario_id == uid) | (Alerta.destinatario == 'Todos') | (Alerta.destinatario == 'Profesores')
        ).order_by(Alerta.fecha_creacion.desc()).all()
    elif rol == 'Estudiante':
        alertas = Alerta.query.filter(
            (Alerta.usuario_id == uid) | (Alerta.destinatario == 'Todos') | (Alerta.destinatario == 'Estudiantes')
        ).order_by(Alerta.fecha_creacion.desc()).all()
    else:
        alertas = Alerta.query.filter_by(usuario_id=uid).order_by(Alerta.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [a.to_dict() for a in alertas]})


@alertas_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or u.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json()
    destinatario = data.get('destinatario', 'Todos')
    if destinatario not in ['Todos', 'Estudiantes', 'Profesores']:
        destinatario = 'Todos'

    if destinatario == 'Todos':
        usuarios = Usuario.query.filter(Usuario.estado == 'Activo').all()
    elif destinatario == 'Estudiantes':
        usuarios = Usuario.query.filter(Usuario.estado == 'Activo').join(Usuario.rol).filter(Usuario.rol.has(nombre='Estudiante')).all()
    elif destinatario == 'Profesores':
        usuarios = Usuario.query.filter(Usuario.estado == 'Activo').join(Usuario.rol).filter(
            Usuario.rol.has(nombre.in_(['Profesor', 'Director de grupo', 'Coordinador']))
        ).all()
    else:
        usuarios = []

    if not usuarios:
        return jsonify({'success': False, 'message': 'No hay usuarios destinatarios'}), 400

    created = []
    for user in usuarios:
        a = Alerta(
            titulo=data['titulo'], descripcion=data.get('descripcion'),
            tipo=data.get('tipo', 'aviso_institucional'),
            usuario_id=user.id, destinatario=destinatario
        )
        db.session.add(a)
        created.append(user.id)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Alerta creada para {len(created)} usuario(s)'}), 201


@alertas_bp.route('/<int:id>/leer', methods=['PUT'])
@jwt_required()
def marcar_leida(id):
    a = Alerta.query.get_or_404(id)
    a.leida = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Marcada como leída'})


@alertas_bp.route('/no-leidas', methods=['GET'])
@jwt_required()
def no_leidas():
    uid = get_jwt_identity()
    return jsonify({'success': True, 'data': {'count': Alerta.query.filter_by(usuario_id=uid, leida=False).count()}})


@alertas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or u.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    a = Alerta.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Alerta eliminada'})
