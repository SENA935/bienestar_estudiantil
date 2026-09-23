from flask import Blueprint, render_template, jsonify
from sqlalchemy import inspect, text

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/api/_diag', methods=['GET'])
def diag():
    from ..extensions import db
    from ..models.usuario import Usuario
    out = {}
    try:
        insp = inspect(db.engine)
        out['tables'] = insp.get_table_names()
        counts = {}
        for t in out['tables']:
            try:
                counts[t] = db.session.execute(text('SELECT COUNT(*) FROM "%s"' % t)).scalar()
            except Exception as e:
                counts[t] = 'ERR: %s' % e
        out['counts'] = counts
    except Exception as e:
        out['tables_err'] = str(e)
    try:
        u = Usuario.query.filter_by(username='admin').first()
        out['admin_found'] = u is not None
        if u:
            out['admin_id'] = u.id
            out['admin_estado'] = u.estado
            try:
                out['admin_checkpw'] = u.check_password('admin123')
            except Exception as e:
                out['admin_checkpw_err'] = str(e)
            try:
                out['admin_todict'] = u.to_dict()
            except Exception as e:
                out['admin_todict_err'] = str(e)
    except Exception as e:
        out['admin_err'] = str(e)
    return jsonify(out)


@pages_bp.route('/')
def index():
    return render_template('inicio.html')


@pages_bp.route('/pausas')
def pausas():
    return render_template('pausas.html')


@pages_bp.route('/login')
def login():
    return render_template('login.html')


@pages_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@pages_bp.route('/instituciones')
def instituciones():
    return render_template('instituciones.html')


@pages_bp.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')


@pages_bp.route('/actividades')
def actividades():
    return render_template('actividades.html')


@pages_bp.route('/programaciones')
def programaciones():
    return render_template('programaciones.html')


@pages_bp.route('/encuestas')
def encuestas():
    return render_template('encuestas.html')


@pages_bp.route('/propuestas')
def propuestas():
    return render_template('propuestas.html')


@pages_bp.route('/alertas')
def alertas():
    return render_template('alertas.html')


@pages_bp.route('/reportes')
def reportes():
    return render_template('reportes.html')


@pages_bp.route('/auditoria')
def auditoria():
    return render_template('auditoria.html')


@pages_bp.route('/cursos')
def cursos():
    return render_template('cursos.html')


@pages_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')


@pages_bp.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')
