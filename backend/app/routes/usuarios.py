from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.rol import Rol
from ..models.auditoria import Auditoria
from ..extensions import db

usuarios_bp = Blueprint('usuarios', __name__)


def _require_role(roles):
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    return u if u and u.rol.nombre in roles else None


@usuarios_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    rol_f = request.args.get('rol', '')
    estado_f = request.args.get('estado', '')
    q = Usuario.query
    if search:
        q = q.filter(db.or_(Usuario.nombre.ilike(f'%{search}%'), Usuario.apellido.ilike(f'%{search}%'), Usuario.email.ilike(f'%{search}%'), Usuario.username.ilike(f'%{search}%')))
    if rol_f:
        q = q.join(Rol).filter(Rol.nombre == rol_f)
    if estado_f:
        q = q.filter(Usuario.estado == estado_f)
    pag = q.order_by(Usuario.fecha_creacion.desc()).paginate(page=page, per_page=per_page)
    return jsonify({'success': True, 'data': {'usuarios': [u.to_dict() for u in pag.items], 'total': pag.total, 'pages': pag.pages, 'current_page': page}})


@usuarios_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    u = _require_role(['Administrador'])
    if not u:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json()
    for f in ['nombre', 'apellido', 'username', 'email', 'password', 'rol_id']:
        if not data.get(f):
            return jsonify({'success': False, 'message': f'Campo {f} requerido'}), 400
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email ya registrado'}), 400
    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username ya existe'}), 400
    nuevo = Usuario(nombre=data['nombre'], apellido=data['apellido'], username=data['username'], email=data['email'], rol_id=data['rol_id'], institucion_id=data.get('institucion_id'), estado=data.get('estado', 'Activo'))
    nuevo.set_password(data['password'])
    db.session.add(nuevo)
    db.session.add(Auditoria(usuario_id=u.id, modulo='Usuarios', accion='CREAR', descripcion=f'Creó usuario {nuevo.username}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario creado', 'data': nuevo.to_dict()}), 201


@usuarios_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    u = _require_role(['Administrador'])
    if not u:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    usr = Usuario.query.get_or_404(id)
    data = request.get_json()
    usr.nombre = data.get('nombre', usr.nombre)
    usr.apellido = data.get('apellido', usr.apellido)
    usr.email = data.get('email', usr.email)
    usr.rol_id = data.get('rol_id', usr.rol_id)
    usr.institucion_id = data.get('institucion_id', usr.institucion_id)
    usr.estado = data.get('estado', usr.estado)
    if data.get('password'):
        usr.set_password(data['password'])
    db.session.add(Auditoria(usuario_id=u.id, modulo='Usuarios', accion='ACTUALIZAR', descripcion=f'Actualizó usuario {usr.username}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario actualizado', 'data': usr.to_dict()})


@usuarios_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    u = _require_role(['Administrador'])
    if not u:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    usr = Usuario.query.get_or_404(id)
    db.session.add(Auditoria(usuario_id=u.id, modulo='Usuarios', accion='ELIMINAR', descripcion=f'Eliminó usuario {usr.username}'))
    db.session.delete(usr)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario eliminado'})


@usuarios_bp.route('/roles', methods=['GET'])
@jwt_required()
def listar_roles():
    return jsonify({'success': True, 'data': [r.to_dict() for r in Rol.query.all()]})
