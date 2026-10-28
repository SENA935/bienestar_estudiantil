from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.encuesta import Encuesta
from ..models.pregunta_encuesta import PreguntaEncuesta
from ..models.opcion_pregunta import OpcionPregunta
from ..models.respuesta_encuesta import RespuestaEncuesta
from ..models.respuesta_pregunta import RespuestaPregunta
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

encuestas_bp = Blueprint('encuestas', __name__)


@encuestas_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    uid = int(get_jwt_identity())
    usuario = Usuario.query.get(uid)
    encuestas = Encuesta.query.order_by(Encuesta.fecha_creacion.desc()).all()
    data = []
    for e in encuestas:
        d = e.to_dict()
        respondidas = RespuestaEncuesta.query.filter_by(encuesta_id=e.id, usuario_id=uid).count()
        d['ya_respondio'] = respondidas > 0
        data.append(d)
    return jsonify({'success': True, 'data': data})


@encuestas_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    data = request.get_json()
    enc = Encuesta(titulo=data['titulo'], descripcion=data.get('descripcion'), estado=data.get('estado', 'Activa'))
    db.session.add(enc)
    db.session.flush()
    for i, pd in enumerate(data.get('preguntas', [])):
        preg = PreguntaEncuesta(encuesta_id=enc.id, texto=pd['texto'], tipo=pd['tipo'], orden=i, requerida=pd.get('requerida', True))
        db.session.add(preg)
        db.session.flush()
        for j, od in enumerate(pd.get('opciones', [])):
            db.session.add(OpcionPregunta(pregunta_id=preg.id, texto=od['texto'], valor=od.get('valor', j), orden=j))
    db.session.add(Auditoria(usuario_id=uid, modulo='Encuestas', accion='CREAR', descripcion=f'Creó encuesta {enc.titulo}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta creada', 'data': enc.to_dict()}), 201


@encuestas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener(id):
    enc = Encuesta.query.get_or_404(id)
    d = enc.to_dict()
    d['preguntas'] = [p.to_dict() for p in enc.preguntas]
    return jsonify({'success': True, 'data': d})


@encuestas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    enc = Encuesta.query.get_or_404(id)
    data = request.get_json()
    enc.titulo = data.get('titulo', enc.titulo)
    enc.descripcion = data.get('descripcion', enc.descripcion)
    enc.estado = data.get('estado', enc.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta actualizada', 'data': enc.to_dict()})


@encuestas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    enc = Encuesta.query.get_or_404(id)
    db.session.delete(enc)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta eliminada'})


@encuestas_bp.route('/<int:id>/responder', methods=['POST'])
@jwt_required()
def responder(id):
    uid = int(get_jwt_identity())
    data = request.get_json()
    re = RespuestaEncuesta(encuesta_id=id, usuario_id=uid)
    db.session.add(re)
    db.session.flush()
    for rd in data.get('respuestas', []):
        db.session.add(RespuestaPregunta(respuesta_encuesta_id=re.id, pregunta_id=rd['pregunta_id'], opcion_id=rd.get('opcion_id'), valor_texto=rd.get('valor_texto'), valor_numero=rd.get('valor_numero')))
    db.session.add(Auditoria(usuario_id=uid, modulo='Encuestas', accion='RESPONDER', descripcion=f'Respondió encuesta {id}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Respuesta guardada'}), 201


@encuestas_bp.route('/<int:id>/resultados', methods=['GET'])
@jwt_required()
def resultados(id):
    return jsonify({'success': True, 'data': [r.to_dict() for r in RespuestaEncuesta.query.filter_by(encuesta_id=id).all()]})
