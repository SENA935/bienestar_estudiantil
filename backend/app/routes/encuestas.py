from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.encuesta import Encuesta, PreguntaEncuesta, OpcionPregunta
from ..models.respuesta import RespuestaEncuesta, RespuestaPregunta
from ..models.auditoria import Auditoria
from ..extensions import db

encuestas_bp = Blueprint('encuestas', __name__)


@encuestas_bp.route('', methods=['GET'])
@jwt_required()
def get_encuestas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    estado = request.args.get('estado', '')

    query = Encuesta.query
    if estado:
        query = query.filter_by(estado=estado)

    pagination = query.order_by(Encuesta.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'success': True,
        'data': {
            'encuestas': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })


@encuestas_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_encuestas():
    encuestas = Encuesta.query.filter_by(estado='Activa').all()
    return jsonify({'success': True, 'data': [e.to_dict() for e in encuestas]})


@encuestas_bp.route('', methods=['POST'])
@jwt_required()
def create_encuesta():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    data = request.get_json()
    if not data.get('titulo'):
        return jsonify({'success': False, 'message': 'Título es requerido'}), 400

    enc = Encuesta(
        titulo=data['titulo'],
        descripcion=data.get('descripcion'),
        estado=data.get('estado', 'Activa')
    )
    db.session.add(enc)
    db.session.flush()

    for preg_data in data.get('preguntas', []):
        preg = PreguntaEncuesta(
            encuesta_id=enc.id,
            texto=preg_data['texto'],
            tipo=preg_data['tipo'],
            orden=preg_data.get('orden', 0),
            requerida=preg_data.get('requerida', True)
        )
        db.session.add(preg)
        db.session.flush()

        for opc_data in preg_data.get('opciones', []):
            opc = OpcionPregunta(
                pregunta_id=preg.id,
                texto=opc_data['texto'],
                valor=opc_data.get('valor', 0),
                orden=opc_data.get('orden', 0)
            )
            db.session.add(opc)

    aud = Auditoria(usuario_id=user_id, modulo='Encuestas', accion='CREAR',
                    descripcion=f'Encuesta creada: {enc.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta creada correctamente', 'data': enc.to_dict()}), 201


@encuestas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_encuesta(id):
    enc = Encuesta.query.get_or_404(id)
    result = enc.to_dict()
    result['preguntas'] = [p.to_dict() for p in enc.preguntas]
    return jsonify({'success': True, 'data': result})


@encuestas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_encuesta(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    enc = Encuesta.query.get_or_404(id)
    data = request.get_json()

    enc.titulo = data.get('titulo', enc.titulo)
    enc.descripcion = data.get('descripcion', enc.descripcion)
    enc.estado = data.get('estado', enc.estado)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta actualizada correctamente', 'data': enc.to_dict()})


@encuestas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_encuesta(id):
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)
    if not user or user.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403

    enc = Encuesta.query.get_or_404(id)
    db.session.delete(enc)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta eliminada correctamente'})


@encuestas_bp.route('/<int:id>/responder', methods=['POST'])
@jwt_required()
def responder_encuesta(id):
    user_id = int(get_jwt_identity())
    enc = Encuesta.query.get_or_404(id)

    if enc.estado != 'Activa':
        return jsonify({'success': False, 'message': 'La encuesta no está activa'}), 400

    data = request.get_json()
    respuestas_data = data.get('respuestas', [])

    resp_enc = RespuestaEncuesta(encuesta_id=id, usuario_id=user_id)
    db.session.add(resp_enc)
    db.session.flush()

    for r in respuestas_data:
        resp_preg = RespuestaPregunta(
            respuesta_encuesta_id=resp_enc.id,
            pregunta_id=r['pregunta_id'],
            opcion_id=r.get('opcion_id'),
            texto_respuesta=r.get('texto_respuesta'),
            valor_numerico=r.get('valor_numerico')
        )
        db.session.add(resp_preg)

    aud = Auditoria(usuario_id=user_id, modulo='Encuestas', accion='RESPONDER',
                    descripcion=f'Encuesta respondida: {enc.titulo}', ip=request.remote_addr)
    db.session.add(aud)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Encuesta respondida correctamente'}), 201


@encuestas_bp.route('/<int:id>/resultados', methods=['GET'])
@jwt_required()
def resultados_encuesta(id):
    enc = Encuesta.query.get_or_404(id)
    respuestas = RespuestaEncuesta.query.filter_by(encuesta_id=id).all()

    resultados = {}
    for preg in enc.preguntas:
        resultados[preg.id] = {
            'pregunta': preg.texto,
            'tipo': preg.tipo,
            'respuestas_count': 0,
            'opciones_count': {},
            'textos': [],
            'valores': []
        }

    for resp in respuestas:
        for rp in resp.respuestas:
            if rp.pregunta_id in resultados:
                resultados[rp.pregunta_id]['respuestas_count'] += 1
                if rp.opcion_id:
                    key = rp.opcion.texto if rp.opcion else str(rp.opcion_id)
                    resultados[rp.pregunta_id]['opciones_count'][key] = \
                        resultados[rp.pregunta_id]['opciones_count'].get(key, 0) + 1
                if rp.texto_respuesta:
                    resultados[rp.pregunta_id]['textos'].append(rp.texto_respuesta)
                if rp.valor_numerico is not None:
                    resultados[rp.pregunta_id]['valores'].append(rp.valor_numerico)

    return jsonify({
        'success': True,
        'data': {
            'encuesta': enc.to_dict(),
            'total_respuestas': len(respuestas),
            'resultados': resultados
        }
    })
