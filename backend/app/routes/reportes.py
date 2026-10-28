from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from ..models.actividad_realizada import ActividadRealizada
from ..models.respuesta_encuesta import RespuestaEncuesta
from ..models.propuesta import Propuesta
from ..models.programacion import Programacion
from ..models.actividad import Actividad
from ..models.curso import Curso
from ..models.usuario import Usuario
from ..models.rol import Rol
from ..models.categoria_actividad import CategoriaActividad
from ..extensions import db
import csv, io

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('', methods=['GET'])
@jwt_required()
def reportes():
    fi = request.args.get('fecha_inicio')
    ff = request.args.get('fecha_fin')
    solo_profes = request.args.get('solo_profesores', '') == 'true'

    q = ActividadRealizada.query.filter_by(estado='Realizada')
    if fi:
        q = q.filter(ActividadRealizada.fecha >= fi)
    if ff:
        q = q.filter(ActividadRealizada.fecha <= ff)

    if solo_profes:
        q = q.join(Programacion, Programacion.id == ActividadRealizada.programacion_id) \
             .join(Usuario, Usuario.id == Programacion.docente_id) \
             .join(Rol, Rol.id == Usuario.rol_id) \
             .filter(Rol.nombre.in_(['Profesor', 'Director de grupo']))

    resumen_count = q.count()

    if solo_profes:
        por_cat = db.session.query(CategoriaActividad.nombre, func.count(ActividadRealizada.id)) \
            .join(Actividad, Actividad.categoria_id == CategoriaActividad.id) \
            .join(Programacion, Programacion.actividad_id == Actividad.id) \
            .join(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id) \
            .join(Usuario, Usuario.id == Programacion.docente_id) \
            .join(Rol, Rol.id == Usuario.rol_id) \
            .filter(Rol.nombre.in_(['Profesor', 'Director de grupo'])) \
            .group_by(CategoriaActividad.nombre).all()

        por_curso = db.session.query(Curso.nombre, func.count(ActividadRealizada.id)) \
            .join(Programacion, Programacion.curso_id == Curso.id) \
            .join(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id) \
            .join(Usuario, Usuario.id == Programacion.docente_id) \
            .join(Rol, Rol.id == Usuario.rol_id) \
            .filter(Rol.nombre.in_(['Profesor', 'Director de grupo'])) \
            .group_by(Curso.nombre).all()
    else:
        por_cat = db.session.query(CategoriaActividad.nombre, func.count(ActividadRealizada.id)) \
            .join(Actividad, Actividad.categoria_id == CategoriaActividad.id) \
            .join(Programacion, Programacion.actividad_id == Actividad.id) \
            .join(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id) \
            .group_by(CategoriaActividad.nombre).all()

        por_curso = db.session.query(Curso.nombre, func.count(ActividadRealizada.id)) \
            .join(Programacion, Programacion.curso_id == Curso.id) \
            .join(ActividadRealizada, ActividadRealizada.programacion_id == Programacion.id) \
            .group_by(Curso.nombre).all()

    return jsonify({'success': True, 'data': {
        'resumen': {
            'actividades_realizadas': resumen_count,
            'encuestas_respondidas': RespuestaEncuesta.query.count(),
            'total_propuestas': Propuesta.query.count(),
            'propuestas_aprobadas': Propuesta.query.filter_by(estado='Aprobada').count()
        },
        'por_categoria': [{'nombre': n, 'cantidad': c} for n, c in por_cat],
        'por_curso': [{'nombre': n, 'cantidad': c} for n, c in por_curso]
    }})


@reportes_bp.route('/exportar-csv', methods=['GET'])
@jwt_required()
def exportar_csv():
    solo_profes = request.args.get('solo_profesores', '') == 'true'
    q = ActividadRealizada.query.all()
    if solo_profes:
        q = [a for a in q if a.programacion and a.programacion.docente and a.programacion.docente.rol and a.programacion.docente.rol.nombre in ['Profesor', 'Director de grupo']]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fecha', 'Actividad', 'Curso', 'Docente', 'Estado', 'Observaciones'])
    for a in q:
        d = a.to_dict()
        writer.writerow([d.get('fecha', ''), d.get('actividad_titulo', ''), d.get('curso_nombre', ''), d.get('docente_nombre', ''), a.estado, a.observaciones or ''])
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=reporte_actividades.csv'})
