from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.auditoria import Auditoria
from ..models.usuario import Usuario

auditoria_bp = Blueprint('auditoria', __name__)


@auditoria_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or u.rol.nombre not in ['Administrador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    page = request.args.get('page', 1, type=int)
    pag = Auditoria.query.order_by(Auditoria.fecha.desc()).paginate(page=page, per_page=50)
    return jsonify({'success': True, 'data': {'registros': [a.to_dict() for a in pag.items], 'total': pag.total, 'pages': pag.pages, 'current_page': page}})
