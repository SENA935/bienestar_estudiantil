from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.auditoria import Auditoria

auditoria_bp = Blueprint('auditoria', __name__)


@auditoria_bp.route('', methods=['GET'])
@jwt_required()
def get_auditoria():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    modulo = request.args.get('modulo', '')
    accion = request.args.get('accion', '')

    query = Auditoria.query
    if modulo:
        query = query.filter_by(modulo=modulo)
    if accion:
        query = query.filter_by(accion=accion)

    pagination = query.order_by(Auditoria.fecha.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'success': True,
        'data': {
            'registros': [a.to_dict() for a in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })
