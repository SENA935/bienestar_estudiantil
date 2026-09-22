from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Datos no proporcionados'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Usuario y contraseña son requeridos'}), 400

    user = Usuario.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401

    if user.estado != 'Activo':
        return jsonify({'success': False, 'message': 'Usuario inactivo'}), 403

    token = create_access_token(identity=str(user.id))

    auditoria = Auditoria(
        usuario_id=user.id,
        modulo='Auth',
        accion='LOGIN',
        descripcion=f'Inicio de sesión exitoso: {user.username}',
        ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Inicio de sesión exitoso',
        'data': {
            'token': token,
            'user': user.to_dict()
        }
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user = Usuario.query.get(int(user_id))
    if user:
        auditoria = Auditoria(
            usuario_id=user.id,
            modulo='Auth',
            accion='LOGOUT',
            descripcion=f'Cierre de sesión: {user.username}',
            ip=request.remote_addr
        )
        db.session.add(auditoria)
        db.session.commit()

    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = Usuario.query.get(int(user_id))
    if not user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    return jsonify({'success': True, 'data': user.to_dict()})
