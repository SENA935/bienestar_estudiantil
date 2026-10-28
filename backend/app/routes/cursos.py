from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.curso import Curso
from ..models.estudiante import Estudiante
from ..models.programacion import Programacion
from ..models.actividad_realizada import ActividadRealizada
from ..models.usuario import Usuario
from ..models.auditoria import Auditoria
from ..extensions import db

cursos_bp = Blueprint('cursos', __name__)


@cursos_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    grado = request.args.get('grado', '')
    jornada = request.args.get('jornada', '')
    estado = request.args.get('estado', '')
    q = Curso.query
    if search:
        q = q.filter(Curso.nombre.ilike(f'%{search}%'))
    if grado:
        q = q.filter(Curso.grado == grado)
    if jornada:
        q = q.filter(Curso.jornada == jornada)
    if estado:
        q = q.filter(Curso.estado == estado)
    pag = q.order_by(Curso.grado.asc()).paginate(page=page, per_page=per_page)
    return jsonify({'success': True, 'data': {'cursos': [c.to_dict() for c in pag.items], 'total': pag.total, 'pages': pag.pages, 'current_page': page}})


@cursos_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    uid = int(get_jwt_identity())
    u = Usuario.query.get(uid)
    if not u or u.rol.nombre not in ['Administrador', 'Coordinador']:
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
    data = request.get_json()
    c = Curso(nombre=data['nombre'], grado=data['grado'], jornada=data.get('jornada', 'Mañana'), director_grupo=data.get('director_grupo'), estado=data.get('estado', 'Activo'))
    db.session.add(c)
    db.session.add(Auditoria(usuario_id=uid, modulo='Cursos', accion='CREAR', descripcion=f'Creó curso {c.nombre}'))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso creado', 'data': c.to_dict()}), 201


@cursos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    c = Curso.query.get_or_404(id)
    data = request.get_json()
    c.nombre = data.get('nombre', c.nombre)
    c.grado = data.get('grado', c.grado)
    c.jornada = data.get('jornada', c.jornada)
    c.director_grupo = data.get('director_grupo', c.director_grupo)
    c.estado = data.get('estado', c.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso actualizado', 'data': c.to_dict()})


@cursos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    c = Curso.query.get_or_404(id)
    uid = int(get_jwt_identity())
    progs = Programacion.query.filter_by(curso_id=id).all()
    for p in progs:
        ActividadRealizada.query.filter_by(programacion_id=p.id).delete()
    Programacion.query.filter_by(curso_id=id).delete()
    Estudiante.query.filter_by(curso_id=id).delete()
    db.session.add(Auditoria(usuario_id=uid, modulo='Cursos', accion='ELIMINAR', descripcion=f'Eliminó curso {c.nombre}'))
    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Curso eliminado'})


@cursos_bp.route('/<int:id>/estudiantes', methods=['GET'])
@jwt_required()
def listar_estudiantes(id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    q = Estudiante.query.filter_by(curso_id=id)
    if search:
        q = q.filter(db.or_(Estudiante.nombre.ilike(f'%{search}%'), Estudiante.apellido.ilike(f'%{search}%'), Estudiante.documento.ilike(f'%{search}%')))
    pag = q.paginate(page=page, per_page=per_page)
    return jsonify({'success': True, 'data': {'estudiantes': [e.to_dict() for e in pag.items], 'total': pag.total, 'pages': pag.pages, 'current_page': page}})


@cursos_bp.route('/<int:id>/estudiantes', methods=['POST'])
@jwt_required()
def crear_estudiante(id):
    data = request.get_json()
    existente = Estudiante.query.filter_by(documento=data['documento']).first()
    if existente:
        return jsonify({'success': False, 'message': f'El documento {data["documento"]} ya está registrado para {existente.nombre} {existente.apellido}'}), 400
    e = Estudiante(nombre=data['nombre'], apellido=data['apellido'], documento=data['documento'], curso_id=id, estado=data.get('estado', 'Activo'), email=email)
    db.session.add(e)
    db.session.flush()
    email = f"{data['nombre'].lower().split()[0]}.{data['apellido'].lower().split()[0]}@estudiante.colegio.com"
    username = f"{data['nombre'].lower().split()[0]}{data['apellido'].lower().split()[0]}"
    password = data['documento']
    from ..models.usuario import Usuario
    from ..models.rol import Rol
    est_rol = Rol.query.filter_by(nombre='Estudiante').first()
    if est_rol:
        existente_email = Usuario.query.filter_by(email=email).first()
        if existente_email:
            email = f"{data['nombre'].lower().split()[0]}.{data['apellido'].lower().split()[0]}{e.id}@estudiante.colegio.com"
            username = f"{data['nombre'].lower().split()[0]}{data['apellido'].lower().split()[0]}{e.id}"
        u = Usuario(nombre=data['nombre'], apellido=data['apellido'], username=username, email=email, rol_id=est_rol.id)
        u.set_password(password)
        db.session.add(u)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante creado', 'data': e.to_dict(), 'credenciales': {'email': email, 'usuario': username, 'contrasena': password} if est_rol else None}), 201


@cursos_bp.route('/estudiantes/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_estudiante(id):
    e = Estudiante.query.get_or_404(id)
    data = request.get_json()
    if 'documento' in data and data['documento'] != e.documento:
        existente = Estudiante.query.filter_by(documento=data['documento']).first()
        if existente:
            return jsonify({'success': False, 'message': f'El documento {data["documento"]} ya está registrado para {existente.nombre} {existente.apellido}'}), 400
    e.nombre = data.get('nombre', e.nombre)
    e.apellido = data.get('apellido', e.apellido)
    e.documento = data.get('documento', e.documento)
    e.curso_id = data.get('curso_id', e.curso_id)
    e.estado = data.get('estado', e.estado)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante actualizado', 'data': e.to_dict()})


@cursos_bp.route('/estudiantes/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_estudiante(id):
    e = Estudiante.query.get_or_404(id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudiante eliminado'})


@cursos_bp.route('/estudiantes-todos', methods=['GET'])
@jwt_required()
def todos_estudiantes():
    return jsonify({'success': True, 'data': [e.to_dict() for e in Estudiante.query.all()]})
