from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.solicitud_participacion import SolicitudParticipacion
from ..models.usuario import Usuario
from ..models.programacion import Programacion
from ..extensions import db

solicitudes_bp = Blueprint('solicitudes', __name__)


@solicitudes_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    prog = Programacion.query.get_or_404(data['programacion_id'])
    existente = SolicitudParticipacion.query.filter_by(
        estudiante_id=uid, programacion_id=data['programacion_id']
    ).first()
    if existente:
        return jsonify({'success': False, 'message': 'Ya enviaste una solicitud para esta actividad'}), 400
    s = SolicitudParticipacion(
        estudiante_id=uid,
        actividad_id=prog.actividad_id,
        programacion_id=prog.id,
        docente_id=prog.docente_id,
        estado='Pendiente'
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitud enviada al profesor', 'data': s.to_dict()}), 201


@solicitudes_bp.route('/mias', methods=['GET'])
@jwt_required()
def mis_solicitudes():
    uid = int(get_jwt_identity())
    sols = SolicitudParticipacion.query.filter_by(estudiante_id=uid).order_by(SolicitudParticipacion.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in sols]})


@solicitudes_bp.route('/profesor', methods=['GET'])
@jwt_required()
def solicitudes_profesor():
    uid = int(get_jwt_identity())
    sols = SolicitudParticipacion.query.filter_by(docente_id=uid).order_by(SolicitudParticipacion.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in sols]})


@solicitudes_bp.route('/<int:id>/responder', methods=['PUT'])
@jwt_required()
def responder(id):
    uid = int(get_jwt_identity())
    s = SolicitudParticipacion.query.get_or_404(id)
    if s.docente_id != uid:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json()
    s.estado = data.get('estado', s.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitud actualizada', 'data': s.to_dict()})


@solicitudes_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    uid = int(get_jwt_identity())
    s = SolicitudParticipacion.query.get_or_404(id)
    if s.estudiante_id != uid and s.docente_id != uid:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    db.session.delete(s)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Solicitud eliminada'})


@solicitudes_bp.route('/admin', methods=['GET'])
@jwt_required()
def todas():
    sols = SolicitudParticipacion.query.order_by(SolicitudParticipacion.fecha_creacion.desc()).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in sols]})
