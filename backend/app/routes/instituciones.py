from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.institucion import Institucion
from ..models.sede import Sede
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

instituciones_bp = Blueprint('instituciones', __name__)


@instituciones_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    q = Institucion.query
    if search:
        q = q.filter(db.or_(Institucion.nombre.ilike(f'%{search}%'), Institucion.nit.ilike(f'%{search}%')))
    pag = q.order_by(Institucion.fecha_creacion.desc()).paginate(page=page, per_page=per_page)
    return jsonify({'success': True, 'data': {'instituciones': [i.to_dict() for i in pag.items], 'total': pag.total, 'pages': pag.pages, 'current_page': page}})


@instituciones_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or u.rol.nombre not in ['Administrador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json()
    inst = Institucion(nombre=data['nombre'], nit=data.get('nit'), telefono=data.get('telefono'), email=data.get('email'), estado=data.get('estado', 'Activa'))
    db.session.add(inst)
    db.session.add(Auditoria(usuario_id=uid, modulo='Instituciones', accion='CREAR', descripcion=f'Creó institución {inst.nombre}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución creada', 'data': inst.to_dict()}), 201


@instituciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    uid = int(get_jwt_identity())
    inst = Institucion.query.get_or_404(id)
    data = request.get_json()
    inst.nombre = data.get('nombre', inst.nombre)
    inst.nit = data.get('nit', inst.nit)
    inst.telefono = data.get('telefono', inst.telefono)
    inst.email = data.get('email', inst.email)
    inst.estado = data.get('estado', inst.estado)
    db.session.add(Auditoria(usuario_id=uid, modulo='Instituciones', accion='ACTUALIZAR', descripcion=f'Actualizó institución {inst.nombre}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución actualizada', 'data': inst.to_dict()})


@instituciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    uid = int(get_jwt_identity())
    inst = Institucion.query.get_or_404(id)
    db.session.add(Auditoria(usuario_id=uid, modulo='Instituciones', accion='ELIMINAR', descripcion=f'Eliminó institución {inst.nombre}'))
    db.session.delete(inst)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución eliminada'})


@instituciones_bp.route('/<int:id>/sedes', methods=['GET'])
@jwt_required()
def listar_sedes(id):
    return jsonify({'success': True, 'data': [s.to_dict() for s in Sede.query.filter_by(institucion_id=id).all()]})


@instituciones_bp.route('/<int:id>/sedes', methods=['POST'])
@jwt_required()
def crear_sede(id):
    data = request.get_json()
    sede = Sede(nombre=data['nombre'], direccion=data.get('direccion'), institucion_id=id, telefono=data.get('telefono'), estado=data.get('estado', 'Activa'))
    db.session.add(sede)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Sede creada', 'data': sede.to_dict()}), 201
