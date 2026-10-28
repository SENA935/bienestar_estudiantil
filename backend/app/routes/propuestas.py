from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.propuesta import Propuesta
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

propuestas_bp = Blueprint('propuestas', __name__)


@propuestas_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    return jsonify({'success': True, 'data': [p.to_dict() for p in Propuesta.query.order_by(Propuesta.fecha.desc()).all()]})


@propuestas_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    prop = Propuesta(titulo=data['titulo'], descripcion=data['descripcion'], estudiante_id=uid)
    db.session.add(prop)
    db.session.add(Auditoria(usuario_id=uid, modulo='Propuestas', accion='CREAR', descripcion=f'Creó propuesta {prop.titulo}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Propuesta enviada', 'data': prop.to_dict()}), 201


@propuestas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    prop = Propuesta.query.get_or_404(id)
    data = request.get_json()
    if u.rol.nombre in ['Administrador', 'Coordinador']:
        prop.estado = data.get('estado', prop.estado)
        prop.observaciones_coordinador = data.get('observaciones_coordinador', prop.observaciones_coordinador)
    else:
        prop.titulo = data.get('titulo', prop.titulo)
        prop.descripcion = data.get('descripcion', prop.descripcion)
    db.session.add(Auditoria(usuario_id=uid, modulo='Propuestas', accion='ACTUALIZAR', descripcion=f'Actualizó propuesta {prop.titulo}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Propuesta actualizada', 'data': prop.to_dict()})
