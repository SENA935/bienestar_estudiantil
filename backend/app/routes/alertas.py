from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.alerta import Alerta
from ..extensions import db

alertas_bp = Blueprint('alertas', __name__)


@alertas_bp.route('', methods=['GET'])
@jwt_required()
def get_alertas():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get(user_id)

    query = Alerta.query
    if user and user.rol and user.rol.nombre == 'Estudiante':
        query = query.filter_by(usuario_id=user_id)

    alertas = query.order_by(Alerta.fecha.desc()).limit(50).all()
    return jsonify({'success': True, 'data': [a.to_dict() for a in alertas]})


@alertas_bp.route('/<int:id>/leer', methods=['PUT'])
@jwt_required()
def marcar_leida(id):
    alerta = Alerta.query.get_or_404(id)
    alerta.leida = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Alerta marcada como leída'})


@alertas_bp.route('/leer-todas', methods=['PUT'])
@jwt_required()
def marcar_todas_leidas():
    user_id = int(get_jwt_identity())
    Alerta.query.filter_by(usuario_id=user_id, leida=False).update({'leida': True})
    db.session.commit()
    return jsonify({'success': True, 'message': 'Todas las alertas marcadas como leídas'})
