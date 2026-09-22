from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.rol import Rol
from ..models.auditoria import Auditoria
from ..extensions import db

usuarios_bp = Blueprint('usuarios', __name__)


def require_admin():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return None
    return user


@usuarios_bp.route('', methods=['GET'])
@jwt_required()
def get_usuarios():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    rol_filter = request.args.get('rol', '')
    estado_filter = request.args.get('estado', '')

    query = Usuario.query

    if search:
        query = query.filter(
            db.or_(
                Usuario.nombre.ilike(f'%{search}%'),
                Usuario.apellido.ilike(f'%{search}%'),
                Usuario.username.ilike(f'%{search}%'),
                Usuario.email.ilike(f'%{search}%')
            )
        )

    if rol_filter:
        rol = Rol.query.filter_by(nombre=rol_filter).first()
        if rol:
            query = query.filter_by(rol_id=rol.id)

    if estado_filter:
        query = query.filter_by(estado=estado_filter)

    pagination = query.order_by(Usuario.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'usuarios': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })


@usuarios_bp.route('', methods=['POST'])
@jwt_required()
def create_usuario():
    admin = require_admin()
    if not admin:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    required = ['nombre', 'apellido', 'username', 'email', 'password', 'rol_id']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'Campo {field} es requerido'}), 400

    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400

    user = Usuario(
        nombre=data['nombre'],
        apellido=data['apellido'],
        username=data['username'],
        email=data['email'],
        rol_id=data['rol_id'],
        institucion_id=data.get('institucion_id'),
        estado=data.get('estado', 'Activo')
    )
    user.set_password(data['password'])

    db.session.add(user)
    auditoria = Auditoria(
        usuario_id=admin.id, modulo='Usuarios', accion='CREAR',
        descripcion=f'Usuario creado: {user.username}', ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Usuario creado correctamente', 'data': user.to_dict()}), 201


@usuarios_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    admin = require_admin()
    if not admin:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    user = Usuario.query.get_or_404(id)
    data = request.get_json()

    if 'username' in data and data['username'] != user.username:
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400

    if 'email' in data and data['email'] != user.email:
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400

    user.nombre = data.get('nombre', user.nombre)
    user.apellido = data.get('apellido', user.apellido)
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.rol_id = data.get('rol_id', user.rol_id)
    user.institucion_id = data.get('institucion_id', user.institucion_id)
    user.estado = data.get('estado', user.estado)

    if data.get('password'):
        user.set_password(data['password'])

    auditoria = Auditoria(
        usuario_id=admin.id, modulo='Usuarios', accion='ACTUALIZAR',
        descripcion=f'Usuario actualizado: {user.username}', ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Usuario actualizado correctamente', 'data': user.to_dict()})


@usuarios_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    admin = require_admin()
    if not admin:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    user = Usuario.query.get_or_404(id)
    username = user.username

    auditoria = Auditoria(
        usuario_id=admin.id, modulo='Usuarios', accion='ELIMINAR',
        descripcion=f'Usuario eliminado: {username}', ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})


@usuarios_bp.route('/<int:id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_usuario(id):
    admin = require_admin()
    if not admin:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    user = Usuario.query.get_or_404(id)
    user.estado = 'Inactivo' if user.estado == 'Activo' else 'Activo'

    auditoria = Auditoria(
        usuario_id=admin.id, modulo='Usuarios', accion='ACTUALIZAR',
        descripcion=f'Usuario {user.estado}: {user.username}', ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Usuario {user.estado.lower()} correctamente', 'data': user.to_dict()})
