from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from sqlalchemy import func
from ..models.programacion import Programacion
from ..models.actividad_realizada import ActividadRealizada
from ..models.respuesta_encuesta import RespuestaEncuesta
from ..models.propuesta import Propuesta
from ..models.alerta import Alerta
from ..models.actividad import Actividad
from ..models.curso import Curso
from ..models.categoria_actividad import CategoriaActividad
from ..extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    today = date.today()
    stats = {
        'programaciones_activas': 0,
        'actividades_realizadas': 0,
        'encuestas_respondidas': 0,
        'propuestas_pendientes': 0,
        'alertas_sin_leer': 0
    }
    proximas = []
    por_cat = []
    por_curso = []
    try:
        stats['programaciones_activas'] = Programacion.query.filter(Programacion.estado.in_(['Programada', 'En curso']), Programacion.fecha >= today).count()
    except Exception:
        pass
    try:
        stats['actividades_realizadas'] = ActividadRealizada.query.filter_by(estado='Realizada').count()
    except Exception:
        pass
    try:
        stats['encuestas_respondidas'] = RespuestaEncuesta.query.count()
    except Exception:
        pass
    try:
        stats['propuestas_pendientes'] = Propuesta.query.filter_by(estado='Pendiente').count()
    except Exception:
        pass
    try:
        stats['alertas_sin_leer'] = Alerta.query.filter_by(leida=False).count()
    except Exception:
        pass
    try:
        proximas = Programacion.query.filter(Programacion.fecha >= today, Programacion.estado.in_(['Programada', 'En curso'])).order_by(Programacion.fecha.asc(), Programacion.hora_inicio.asc()).limit(5).all()
    except Exception:
        pass
    try:
        por_cat = db.session.query(CategoriaActividad.nombre, func.count(Actividad.id)).join(Actividad, Actividad.categoria_id == CategoriaActividad.id).group_by(CategoriaActividad.nombre).all()
        if not por_cat:
            por_cat = db.session.query(CategoriaActividad.nombre, func.count(ActividadRealizada.id)).join(Actividad, Actividad.categoria_id == CategoriaActividad.id).join(Programacion, Programacion.actividad_id == Actividad.id).outerjoin(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id).group_by(CategoriaActividad.nombre).all()
    except Exception:
        pass
    try:
        por_curso = db.session.query(Curso.nombre, func.count(Programacion.id)).join(Programacion, Programacion.curso_id == Curso.id).group_by(Curso.nombre).all()
        if not por_curso:
            por_curso = db.session.query(Curso.nombre, func.count(ActividadRealizada.id)).join(Programacion, Programacion.curso_id == Curso.id).outerjoin(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id).group_by(Curso.nombre).all()
    except Exception:
        pass
    return jsonify({'success': True, 'data': {
        'estadisticas': stats,
        'proximas_programaciones': [p.to_dict() for p in proximas],
        'actividades_por_categoria': [{'nombre': n, 'cantidad': c} for n, c in por_cat],
        'participacion_por_curso': [{'nombre': n, 'cantidad': c} for n, c in por_curso]
    }})
