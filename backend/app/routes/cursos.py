from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.curso import Curso
from ..models.estudiante import Estudiante
from ..models.auditoria import Auditoria
from ..extensions import db

cursos_bp = Blueprint('cursos', __name__)


@cursos_bp.route('', methods=['GET'])
@jwt_required()
def get_cursos():
    search = request.args.get('search', '')
    query = Curso.query
    if search:
        query = query.filter(Curso.nombre.ilike(f'%{search}%'))
    cursos = query.order_by(Curso.grado.asc(), Curso.nombre.asc()).all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in cursos]})


@cursos_bp.route('', methods=['POST'])
@jwt_required()
def create_curso():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('nombre') or not data.get('grado'):
        return jsonify({'success': False, 'message': 'Nombre y grado son requeridos'}), 400

    curso = Curso(
        nombre=data['nombre'], grado=data['grado'],
        jornada=data.get('jornada', 'Mañana'),
        director_grupo=data.get('director_grupo'),
        estado=data.get('estado', 'Activo')
    )
    db.session.add(curso)
    aud = Auditoria(usuario_id=user_id, modulo='Cursos', accion='CREAR',
                    descripcion=f'Curso creado: {curso.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso creado correctamente', 'data': curso.to_dict()}), 201


@cursos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_curso(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    curso = Curso.query.get_or_404(id)
    data = request.get_json()

    curso.nombre = data.get('nombre', curso.nombre)
    curso.grado = data.get('grado', curso.grado)
    curso.jornada = data.get('jornada', curso.jornada)
    curso.director_grupo = data.get('director_grupo', curso.director_grupo)
    curso.estado = data.get('estado', curso.estado)

    aud = Auditoria(usuario_id=user_id, modulo='Cursos', accion='ACTUALIZAR',
                    descripcion=f'Curso actualizado: {curso.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso actualizado correctamente', 'data': curso.to_dict()})


@cursos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_curso(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre != 'Administrador':
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    curso = Curso.query.get_or_404(id)
    aud = Auditoria(usuario_id=user_id, modulo='Cursos', accion='ELIMINAR',
                    descripcion=f'Curso eliminado: {curso.nombre}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.delete(curso)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso eliminado correctamente'})


@cursos_bp.route('/<int:id>/estudiantes', methods=['GET'])
@jwt_required()
def get_estudiantes(id):
    estudiantes = Estudiante.query.filter_by(curso_id=id).all()
    return jsonify({'success': True, 'data': [e.to_dict() for e in estudiantes]})


@cursos_bp.route('/<int:id>/estudiantes', methods=['POST'])
@jwt_required()
def create_estudiante(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador', 'Docente']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('nombre') or not data.get('apellido') or not data.get('documento'):
        return jsonify({'success': False, 'message': 'Nombre, apellido y documento son requeridos'}), 400

    if Estudiante.query.filter_by(documento=data['documento']).first():
        return jsonify({'success': False, 'message': 'El documento ya está registrado'}), 400

    est = Estudiante(
        nombre=data['nombre'], apellido=data['apellido'],
        documento=data['documento'], curso_id=id,
        estado=data.get('estado', 'Activo')
    )
    db.session.add(est)
    aud = Auditoria(usuario_id=user_id, modulo='Estudiantes', accion='CREAR',
                    descripcion=f'Estudiante creado: {est.nombre} {est.apellido}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante creado correctamente', 'data': est.to_dict()}), 201


@cursos_bp.route('/estudiantes/<int:id>', methods=['PUT'])
@jwt_required()
def update_estudiante(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador', 'Docente']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    est = Estudiante.query.get_or_404(id)
    data = request.get_json()

    est.nombre = data.get('nombre', est.nombre)
    est.apellido = data.get('apellido', est.apellido)
    est.documento = data.get('documento', est.documento)
    est.curso_id = data.get('curso_id', est.curso_id)
    est.estado = data.get('estado', est.estado)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante actualizado correctamente', 'data': est.to_dict()})


@cursos_bp.route('/estudiantes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_estudiante(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    est = Estudiante.query.get_or_404(id)
    db.session.delete(est)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante eliminado correctamente'})
