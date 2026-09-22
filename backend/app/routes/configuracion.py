from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.periodo_academico import PeriodoAcademico
from ..models.categoria_actividad import CategoriaActividad
from ..models.rol import Rol
from ..extensions import db

configuracion_bp = Blueprint('configuracion', __name__)


@configuracion_bp.route('/periodos', methods=['GET'])
@jwt_required()
def get_periodos():
    periodos = PeriodoAcademico.query.order_by(PeriodoAcademico.id.desc()).all()
    return jsonify({'success': True, 'data': [p.to_dict() for p in periodos]})


@configuracion_bp.route('/periodos', methods=['POST'])
@jwt_required()
def create_periodo():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre != 'Administrador':
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    from datetime import datetime
    periodo = PeriodoAcademico(
        nombre=data['nombre'],
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
        estado=data.get('estado', 'Activo')
    )
    db.session.add(periodo)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Periodo creado correctamente', 'data': periodo.to_dict()}), 201


@configuracion_bp.route('/categorias', methods=['GET'])
@jwt_required()
def get_categorias():
    cats = CategoriaActividad.query.all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in cats]})


@configuracion_bp.route('/categorias', methods=['POST'])
@jwt_required()
def create_categoria():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    cat = CategoriaActividad(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        color=data.get('color', '#3B82F6')
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Categoría creada correctamente', 'data': cat.to_dict()}), 201


@configuracion_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Rol.query.all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in roles]})
