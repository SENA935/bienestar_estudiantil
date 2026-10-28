from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.programacion import Programacion
from ..models.actividad_realizada import ActividadRealizada
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

programaciones_bp = Blueprint('programaciones', __name__)


@programaciones_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    estado = request.args.get('estado', '')
    q = Programacion.query
    if estado:
        q = q.filter_by(estado=estado)
    return jsonify({'success': True, 'data': {'programaciones': [p.to_dict() for p in q.order_by(Programacion.fecha.desc()).all()]}})


@programaciones_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    p = Programacion(actividad_id=data['actividad_id'], curso_id=data['curso_id'], docente_id=data.get('docente_id'), fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(), hora_inicio=datetime.strptime(data['hora_inicio'], '%H:%M').time(), hora_final=datetime.strptime(data['hora_final'], '%H:%M').time() if data.get('hora_final') else None, lugar=data.get('lugar'), estado=data.get('estado', 'Programada'))
    db.session.add(p)
    db.session.add(Auditoria(usuario_id=uid, modulo='Programaciones', accion='CREAR', descripcion=f'Creó programación para {p.fecha}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación creada', 'data': p.to_dict()}), 201


@programaciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    p = Programacion.query.get_or_404(id)
    data = request.get_json()
    p.actividad_id = data.get('actividad_id', p.actividad_id)
    p.curso_id = data.get('curso_id', p.curso_id)
    p.docente_id = data.get('docente_id', p.docente_id)
    if data.get('fecha'):
        p.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    if data.get('hora_inicio'):
        p.hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
    if data.get('hora_final'):
        p.hora_final = datetime.strptime(data['hora_final'], '%H:%M').time()
    p.lugar = data.get('lugar', p.lugar)
    p.estado = data.get('estado', p.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación actualizada', 'data': p.to_dict()})


@programaciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    p = Programacion.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación eliminada'})


@programaciones_bp.route('/registrar-actividad', methods=['POST'])
@jwt_required()
def registrar_actividad():
    data = request.get_json()
    ar = ActividadRealizada(programacion_id=data['programacion_id'], fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(), hora_inicio=datetime.strptime(data['hora_inicio'], '%H:%M').time() if data.get('hora_inicio') else None, hora_final=datetime.strptime(data['hora_final'], '%H:%M').time() if data.get('hora_final') else None, observaciones=data.get('observaciones'), estado=data.get('estado', 'Realizada'))
    db.session.add(ar)
    prog = Programacion.query.get(data['programacion_id'])
    if prog:
        prog.estado = 'Finalizada'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad realizada registrada', 'data': ar.to_dict()}), 201


@programaciones_bp.route('/realizadas', methods=['GET'])
@jwt_required()
def listar_realizadas():
    return jsonify({'success': True, 'data': [r.to_dict() for r in ActividadRealizada.query.order_by(ActividadRealizada.fecha.desc()).all()]})
