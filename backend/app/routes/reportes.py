from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from sqlalchemy import func
from ..models.actividad import Actividad
from ..models.programacion import Programacion
from ..models.encuesta import Encuesta
from ..models.respuesta import RespuestaEncuesta
from ..models.propuesta import Propuesta
from ..models.alerta import Alerta
from ..models.curso import Curso
from ..extensions import db

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('', methods=['GET'])
@jwt_required()
def get_reportes():
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    curso_id = request.args.get('curso_id', '')
    categoria = request.args.get('categoria', '')
    estado = request.args.get('estado', '')

    query_prog = Programacion.query
    if fecha_inicio:
        query_prog = query_prog.filter(Programacion.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d').date())
    if fecha_fin:
        query_prog = query_prog.filter(Programacion.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d').date())
    if curso_id:
        query_prog = query_prog.filter_by(curso_id=int(curso_id))
    if estado:
        query_prog = query_prog.filter_by(estado=estado)

    actividades_realizadas = query_prog.filter_by(estado='Finalizada').count()
    actividades_programadas = query_prog.filter_by(estado='Programada').count()
    actividades_canceladas = query_prog.filter_by(estado='Cancelada').count()
    total_programaciones = query_prog.count()

    participacion = db.session.query(
        Curso.nombre, func.count(Programacion.id)
    ).join(Programacion, Programacion.curso_id == Curso.id)

    if fecha_inicio:
        participacion = participacion.filter(Programacion.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d').date())
    if fecha_fin:
        participacion = participacion.filter(Programacion.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d').date())

    participacion = participacion.group_by(Curso.nombre).all()

    cat_data = db.session.query(
        Actividad.categoria, func.count(Programacion.id)
    ).join(Programacion, Programacion.actividad_id == Actividad.id)

    if categoria:
        cat_data = cat_data.filter(Actividad.categoria == categoria)
    cat_data = cat_data.group_by(Actividad.categoria).all()

    encuestas_respondidas = RespuestaEncuesta.query.count()

    propuestas_stats = db.session.query(
        Propuesta.estado, func.count(Propuesta.id)
    ).group_by(Propuesta.estado).all()

    alertas_count = Alerta.query.count()

    return jsonify({
        'success': True,
        'data': {
            'actividades_realizadas': actividades_realizadas,
            'actividades_programadas': actividades_programadas,
            'actividades_canceladas': actividades_canceladas,
            'total_programaciones': total_programaciones,
            'participacion_por_curso': [{'curso': c, 'total': t} for c, t in participacion],
            'actividades_por_categoria': [{'categoria': c, 'total': t} for c, t in cat_data],
            'encuestas_respondidas': encuestas_respondidas,
            'propuestas_por_estado': [{'estado': e, 'total': t} for e, t in propuestas_stats],
            'alertas_count': alertas_count
        }
    })
