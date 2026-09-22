from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.institucion import Institucion
from ..models.sede import Sede
from ..models.auditoria import Auditoria
from ..extensions import db

instituciones_bp = Blueprint('instituciones', __name__)


@instituciones_bp.route('', methods=['GET'])
@jwt_required()
def get_instituciones():
    search = request.args.get('search', '')
    query = Institucion.query
    if search:
        query = query.filter(
            db.or_(
                Institucion.nombre.ilike(f'%{search}%'),
                Institucion.nit.ilike(f'%{search}%')
            )
        )
    insts = query.order_by(Institucion.id.desc()).all()
    return jsonify({'success': True, 'data': [i.to_dict() for i in insts]})


@instituciones_bp.route('', methods=['POST'])
@jwt_required()
def create_institucion():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('nombre') or not data.get('nit'):
        return jsonify({'success': False, 'message': 'Nombre y NIT son requeridos'}), 400

    if Institucion.query.filter_by(nit=data['nit']).first():
        return jsonify({'success': False, 'message': 'El NIT ya está registrado'}), 400

    inst = Institucion(
        nombre=data['nombre'], nit=data['nit'],
        telefono=data.get('telefono'), email=data.get('email'),
        estado=data.get('estado', 'Activa')
    )
    db.session.add(inst)
    aud = Auditoria(usuario_id=user_id, modulo='Instituciones', accion='CREAR',
                    descripcion=f'Institución creada: {inst.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución creada correctamente', 'data': inst.to_dict()}), 201


@instituciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_institucion(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    inst = Institucion.query.get_or_404(id)
    data = request.get_json()

    inst.nombre = data.get('nombre', inst.nombre)
    inst.nit = data.get('nit', inst.nit)
    inst.telefono = data.get('telefono', inst.telefono)
    inst.email = data.get('email', inst.email)
    inst.estado = data.get('estado', inst.estado)

    aud = Auditoria(usuario_id=user_id, modulo='Instituciones', accion='ACTUALIZAR',
                    descripcion=f'Institución actualizada: {inst.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución actualizada correctamente', 'data': inst.to_dict()})


@instituciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_institucion(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre != 'Administrador':
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    inst = Institucion.query.get_or_404(id)
    aud = Auditoria(usuario_id=user_id, modulo='Instituciones', accion='ELIMINAR',
                    descripcion=f'Institución eliminada: {inst.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.delete(inst)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Institución eliminada correctamente'})


@instituciones_bp.route('/<int:id>/sedes', methods=['GET'])
@jwt_required()
def get_sedes(id):
    sedes = Sede.query.filter_by(institucion_id=id).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in sedes]})


@instituciones_bp.route('/<int:id>/sedes', methods=['POST'])
@jwt_required()
def create_sede(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('nombre'):
        return jsonify({'success': False, 'message': 'Nombre es requerido'}), 400

    sede = Sede(
        nombre=data['nombre'], direccion=data.get('direccion'),
        institucion_id=id, telefono=data.get('telefono'),
        estado=data.get('estado', 'Activa')
    )
    db.session.add(sede)
    aud = Auditoria(usuario_id=user_id, modulo='Sedes', accion='CREAR',
                    descripcion=f'Sede creada: {sede.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Sede creada correctamente', 'data': sede.to_dict()}), 201
