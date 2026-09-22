from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import func
from ..models.programacion import Programacion
from ..models.actividad import Actividad
from ..models.encuesta import Encuesta
from ..models.respuesta import RespuestaEncuesta
from ..models.propuesta import Propuesta
from ..models.alerta import Alerta
from ..models.usuario import Usuario
from ..extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)

    today = date.today()

    programaciones_activas = Programacion.query.filter(
        Programacion.estado.in_(['Programada', 'En curso']),
        Programacion.fecha >= today
    ).count()

    actividades_realizadas = Programacion.query.filter(
        Programacion.estado == 'Finalizada'
    ).count()

    encuestas_respondidas = RespuestaEncuesta.query.count()

    propuestas_pendientes = Propuesta.query.filter(
        Propuesta.estado.in_(['Pendiente', 'En evaluación'])
    ).count()

    alertas_sin_leer = Alerta.query.filter_by(leida=False).count()
    if user and user.rol and user.rol.nombre == 'Estudiante':
        alertas_sin_leer = Alerta.query.filter_by(leida=False, usuario_id=user_id).count()

    proximas = Programacion.query.filter(
        Programacion.fecha >= today,
        Programacion.estado.in_(['Programada', 'En curso'])
    ).order_by(Programacion.fecha.asc(), Programacion.hora_inicio.asc()).limit(10).all()

    cat_data = db.session.query(
        Actividad.categoria,
        func.count(Programacion.id)
    ).join(Programacion, Programacion.actividad_id == Actividad.id).filter(
        Programacion.estado == 'Finalizada'
    ).group_by(Actividad.categoria).all()

    categorias = []
    categorias_valores = []
    for cat, count in cat_data:
        categorias.append(cat)
        categorias_valores.append(count)

    if not cat_data:
        categorias = ['Salud física', 'Salud mental', 'Recreación', 'Cultura', 'Pausas activas']
        categorias_valores = [0, 0, 0, 0, 0]

    from ..models.curso import Curso

    curso_data = db.session.query(
        Curso.nombre,
        func.count(Programacion.id)
    ).join(Programacion, Programacion.curso_id == Curso.id).filter(
        Programacion.estado == 'Finalizada'
    ).group_by(Curso.nombre).all()

    all_cursos = Curso.query.filter_by(estado='Activo').all()
    curso_nombres = [c.nombre for c in all_cursos[:7]]
    curso_valores = []
    for cn in curso_nombres:
        found = False
        for label, count in curso_data:
            if cn == label:
                curso_valores.append(count)
                found = True
                break
        if not found:
            curso_valores.append(0)

    return jsonify({
        'success': True,
        'data': {
            'programaciones_activas': programaciones_activas,
            'actividades_realizadas': actividades_realizadas,
            'encuestas_respondidas': encuestas_respondidas,
            'propuestas_pendientes': propuestas_pendientes,
            'alertas_sin_leer': alertas_sin_leer,
            'proximas_actividades': [p.to_dict() for p in proximas],
            'categorias_actividades': categorias,
            'categorias_valores': categorias_valores,
            'cursos_nombres': curso_nombres,
            'cursos_valores': curso_valores
        }
    })
