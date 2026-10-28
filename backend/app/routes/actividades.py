from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.actividad import Actividad
from ..models.categoria_actividad import CategoriaActividad
from ..models.programacion import Programacion
from ..models.actividad_realizada import ActividadRealizada
from ..models.estudiante import Estudiante
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

actividades_bp = Blueprint('actividades', __name__)


@actividades_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    search = request.args.get('search', '')
    cat = request.args.get('categoria', '')
    q = Actividad.query
    if search:
        q = q.filter(Actividad.titulo.ilike(f'%{search}%'))
    if cat:
        q = q.join(CategoriaActividad).filter(CategoriaActividad.nombre == cat)
    items = q.order_by(Actividad.fecha_creacion.desc()).all()
    data = []
    for a in items:
        d = a.to_dict()
        progs = Programacion.query.filter_by(actividad_id=a.id).all()
        d['programaciones_count'] = len(progs)
        participantes = []
        for p in progs:
            curso = p.curso
            if curso:
                estudiantes = Estudiante.query.filter_by(curso_id=curso.id, estado='Activo').all()
                for est in estudiantes:
                    nombre_completo = f'{est.nombre} {est.apellido}'
                    if nombre_completo not in participantes:
                        participantes.append(nombre_completo)
            if p.docente:
                docente_nombre = f'{p.docente.nombre} {p.docente.apellido}'
                if docente_nombre not in participantes:
                    participantes.append(docente_nombre)
        d['participantes'] = participantes
        d['participantes_count'] = len(participantes)
        data.append(d)
    return jsonify({'success': True, 'data': {'actividades': data}})


@actividades_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    a = Actividad(titulo=data['titulo'], descripcion=data.get('descripcion'), categoria_id=data['categoria_id'], duracion=data.get('duracion', 30), instrucciones=data.get('instrucciones'), estado=data.get('estado', 'Activa'))
    db.session.add(a)
    db.session.add(Auditoria(usuario_id=uid, modulo='Actividades', accion='CREAR', descripcion=f'Creó actividad {a.titulo}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad creada', 'data': a.to_dict()}), 201


@actividades_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    a = Actividad.query.get_or_404(id)
    data = request.get_json()
    a.titulo = data.get('titulo', a.titulo)
    a.descripcion = data.get('descripcion', a.descripcion)
    a.categoria_id = data.get('categoria_id', a.categoria_id)
    a.duracion = data.get('duracion', a.duracion)
    a.instrucciones = data.get('instrucciones', a.instrucciones)
    a.estado = data.get('estado', a.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad actualizada', 'data': a.to_dict()})


@actividades_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    uid = int(get_jwt_identity())
    a = Actividad.query.get_or_404(id)
    db.session.add(Auditoria(usuario_id=uid, modulo='Actividades', accion='ELIMINAR', descripcion=f'Eliminó actividad {a.titulo}'))
    db.session.delete(a)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Actividad eliminada'})


@actividades_bp.route('/categorias', methods=['GET'])
@jwt_required()
def listar_categorias():
    return jsonify({'success': True, 'data': [c.to_dict() for c in CategoriaActividad.query.all()]})


@actividades_bp.route('/categorias', methods=['POST'])
@jwt_required()
def crear_categoria():
    data = request.get_json()
    c = CategoriaActividad(nombre=data['nombre'], descripcion=data.get('descripcion'), color=data.get('color', '#087f8c'))
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Categoría creada', 'data': c.to_dict()}), 201
