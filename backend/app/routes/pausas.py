from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.pausa_activa import PausaActiva
from ..models.auditoria import Auditoria
from ..extensions import db

pausas_bp = Blueprint('pausas', __name__)


@pausas_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    pausas = PausaActiva.query.filter_by(estado='Activa').order_by(PausaActiva.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [p.to_dict() for p in pausas]})


@pausas_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    p = PausaActiva(
        nombre=data['nombre'], descripcion=data.get('descripcion'),
        instrucciones=data.get('instrucciones'),
        duracion_segundos=data.get('duracion_segundos', 180),
        dificultad=data.get('dificultad', 'Facil'),
        color=data.get('color', '#087f8c'),
        bg_gradient=data.get('bg_gradient', 'linear-gradient(135deg,#dcfce7,#a5f3fc)'),
        icono=data.get('icono', 'fa-heart'),
        video_url=data.get('video_url'),
        estado=data.get('estado', 'Activa'),
        creado_por=uid
    )
    db.session.add(p)
    db.session.add(Auditoria(usuario_id=uid, modulo='Pausas Activas', accion='CREAR', descripcion=f'Creó pausa activa {p.nombre}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Pausa activa creada', 'data': p.to_dict()}), 201


@pausas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    uid = int(get_jwt_identity())
    p = PausaActiva.query.get_or_404(id)
    data = request.get_json()
    p.nombre = data.get('nombre', p.nombre)
    p.descripcion = data.get('descripcion', p.descripcion)
    p.instrucciones = data.get('instrucciones', p.instrucciones)
    p.duracion_segundos = data.get('duracion_segundos', p.duracion_segundos)
    p.dificultad = data.get('dificultad', p.dificultad)
    p.color = data.get('color', p.color)
    p.bg_gradient = data.get('bg_gradient', p.bg_gradient)
    p.icono = data.get('icono', p.icono)
    p.video_url = data.get('video_url', p.video_url)
    p.estado = data.get('estado', p.estado)
    db.session.add(Auditoria(usuario_id=uid, modulo='Pausas Activas', accion='ACTUALIZAR', descripcion=f'Actualizó pausa activa {p.nombre}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Pausa activa actualizada', 'data': p.to_dict()})


@pausas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    uid = int(get_jwt_identity())
    p = PausaActiva.query.get_or_404(id)
    db.session.add(Auditoria(usuario_id=uid, modulo='Pausas Activas', accion='ELIMINAR', descripcion=f'Eliminó pausa activa {p.nombre}'))
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Pausa activa eliminada'})


@pausas_bp.route('/todas', methods=['GET'])
@jwt_required()
def todas():
    pausas = PausaActiva.query.order_by(PausaActiva.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [p.to_dict() for p in pausas]})
