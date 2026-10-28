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
        return jsonify({'success': False, 'message': 'Datos requeridos'}), 400
    email = data.get('email', '').strip()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401
    if usuario.estado != 'Activo':
        return jsonify({'success': False, 'message': 'Usuario inactivo'}), 403
    token = create_access_token(identity=str(usuario.id))
    db.session.add(Auditoria(usuario_id=usuario.id, modulo='Auth', accion='LOGIN', descripcion='Inicio de sesión', ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inicio de sesión exitoso', 'data': {'token': token, 'usuario': usuario.to_dict()}})


@auth_bp.route('/recuperar-contrasena', methods=['POST'])
def recuperar_contrasena():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Datos requeridos'}), 400
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Correo electrónico requerido'}), 400
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'success': True, 'message': 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.'})
    db.session.add(Auditoria(usuario_id=usuario.id, modulo='Auth', accion='RECUPERAR_PASS', descripcion='Solicitud de recuperación de contraseña', ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Se han enviado las instrucciones al correo electrónico.'})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    u = Usuario.query.get(int(get_jwt_identity()))
    if not u:
        return jsonify({'success': False, 'message': 'No encontrado'}), 404
    return jsonify({'success': True, 'data': u.to_dict()})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    uid = int(get_jwt_identity())
    db.session.add(Auditoria(usuario_id=uid, modulo='Auth', accion='LOGOUT', descripcion='Cierre de sesión', ip_address=request.remote_addr))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Sesión cerrada'})


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    uid = int(get_jwt_identity())
    data = request.get_json()
    u = Usuario.query.get(uid)
    if not u.check_password(data.get('current_password', '')):
        return jsonify({'success': False, 'message': 'Contraseña actual incorrecta'}), 400
    if len(data.get('new_password', '')) < 6:
        return jsonify({'success': False, 'message': 'Mínimo 6 caracteres'}), 400
    u.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contraseña actualizada'})
