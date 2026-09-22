from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..extensions import db

perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('', methods=['GET'])
@jwt_required()
def get_perfil():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get_or_404(user_id)
    return jsonify({'success': True, 'data': user.to_dict()})


@perfil_bp.route('', methods=['PUT'])
@jwt_required()
def update_perfil():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get_or_404(user_id)
    data = request.get_json()

    user.nombre = data.get('nombre', user.nombre)
    user.apellido = data.get('apellido', user.apellido)
    user.email = data.get('email', user.email)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Perfil actualizado correctamente', 'data': user.to_dict()})


@perfil_bp.route('/cambiar-password', methods=['PUT'])
@jwt_required()
def cambiar_password():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get_or_404(user_id)
    data = request.get_json()

    if not data.get('password_actual') or not data.get('password_nuevo'):
        return jsonify({'success': False, 'message': 'Contraseña actual y nueva son requeridas'}), 400

    if not user.check_password(data['password_actual']):
        return jsonify({'success': False, 'message': 'La contraseña actual es incorrecta'}), 400

    user.set_password(data['password_nuevo'])
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contraseña cambiada correctamente'})
