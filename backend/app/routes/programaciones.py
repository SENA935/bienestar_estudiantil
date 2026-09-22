from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.usuario import Usuario
from ..models.programacion import Programacion
from ..models.auditoria import Auditoria
from ..extensions import db

programaciones_bp = Blueprint('programaciones', __name__)


@programaciones_bp.route('', methods=['GET'])
@jwt_required()
def get_programaciones():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    estado = request.args.get('estado', '')
    curso_id = request.args.get('curso_id', '', type=str)

    query = Programacion.query
    if estado:
        query = query.filter_by(estado=estado)
    if curso_id:
        query = query.filter_by(curso_id=int(curso_id))

    pagination = query.order_by(Programacion.fecha.desc(), Programacion.hora_inicio.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'success': True,
        'data': {
            'programaciones': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })


@programaciones_bp.route('', methods=['POST'])
@jwt_required()
def create_programacion():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    required = ['actividad_id', 'curso_id', 'fecha', 'hora_inicio', 'hora_final']
    for f in required:
        if not data.get(f):
            return jsonify({'success': False, 'message': f'Campo {f} es requerido'}), 400

    prog = Programacion(
        actividad_id=data['actividad_id'],
        curso_id=data['curso_id'],
        docente_id=data.get('docente_id'),
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        hora_inicio=datetime.strptime(data['hora_inicio'], '%H:%M').time(),
        hora_final=datetime.strptime(data['hora_final'], '%H:%M').time(),
        lugar=data.get('lugar'),
        estado=data.get('estado', 'Programada')
    )
    db.session.add(prog)
    aud = Auditoria(usuario_id=user_id, modulo='Programaciones', accion='CREAR',
                    descripcion=f'Programación creada para fecha {prog.fecha}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación creada correctamente', 'data': prog.to_dict()}), 201


@programaciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_programacion(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    prog = Programacion.query.get_or_404(id)
    data = request.get_json()

    prog.actividad_id = data.get('actividad_id', prog.actividad_id)
    prog.curso_id = data.get('curso_id', prog.curso_id)
    prog.docente_id = data.get('docente_id', prog.docente_id)
    if data.get('fecha'):
        prog.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    if data.get('hora_inicio'):
        prog.hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
    if data.get('hora_final'):
        prog.hora_final = datetime.strptime(data['hora_final'], '%H:%M').time()
    prog.lugar = data.get('lugar', prog.lugar)
    prog.estado = data.get('estado', prog.estado)

    aud = Auditoria(usuario_id=user_id, modulo='Programaciones', accion='ACTUALIZAR',
                    descripcion=f'Programación #{prog.id} actualizada', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación actualizada correctamente', 'data': prog.to_dict()})


@programaciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_programacion(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    prog = Programacion.query.get_or_404(id)
    aud = Auditoria(usuario_id=user_id, modulo='Programaciones', accion='ELIMINAR',
                    descripcion=f'Programación #{prog.id} eliminada', ip=request.remote_addr)
    db.session.add(aud)
    db.session.delete(prog)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Programación eliminada correctamente'})
