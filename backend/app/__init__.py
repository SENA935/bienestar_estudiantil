import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import Config
from .extensions import db, migrate


def handle_exception(e):
    from flask import jsonify
    return jsonify({'success': False, 'message': str(e)}), 500

def create_app(config_class=Config):
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)
    JWTManager(app)

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': 'No encontrado'}), 404

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.usuarios import usuarios_bp
    from .routes.instituciones import instituciones_bp
    from .routes.cursos import cursos_bp
    from .routes.actividades import actividades_bp
    from .routes.programaciones import programaciones_bp
    from .routes.encuestas import encuestas_bp
    from .routes.propuestas import propuestas_bp
    from .routes.alertas import alertas_bp
    from .routes.reportes import reportes_bp
    from .routes.auditoria import auditoria_bp
    from .routes.pausas import pausas_bp
    from .routes.solicitudes import solicitudes_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(instituciones_bp, url_prefix='/api/instituciones')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(actividades_bp, url_prefix='/api/actividades')
    app.register_blueprint(programaciones_bp, url_prefix='/api/programaciones')
    app.register_blueprint(encuestas_bp, url_prefix='/api/encuestas')
    app.register_blueprint(propuestas_bp, url_prefix='/api/propuestas')
    app.register_blueprint(alertas_bp, url_prefix='/api/alertas')
    app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    app.register_blueprint(auditoria_bp, url_prefix='/api/auditoria')
    app.register_blueprint(pausas_bp, url_prefix='/api/pausas')
    app.register_blueprint(solicitudes_bp, url_prefix='/api/solicitudes')

    @app.route('/')
    def index():
        return send_from_directory(app.template_folder, 'index.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(app.template_folder, 'login.html')

    @app.route('/dashboard')
    def dashboard_page():
        return send_from_directory(app.template_folder, 'dashboard.html')

    @app.route('/instituciones')
    def instituciones_page():
        return send_from_directory(app.template_folder, 'instituciones.html')

    @app.route('/usuarios')
    def usuarios_page():
        return send_from_directory(app.template_folder, 'usuarios.html')

    @app.route('/cursos')
    def cursos_page():
        return send_from_directory(app.template_folder, 'cursos.html')

    @app.route('/actividades')
    def actividades_page():
        return send_from_directory(app.template_folder, 'actividades.html')

    @app.route('/programaciones')
    def programaciones_page():
        return send_from_directory(app.template_folder, 'programaciones.html')

    @app.route('/encuestas')
    def encuestas_page():
        return send_from_directory(app.template_folder, 'encuestas.html')

    @app.route('/propuestas')
    def propuestas_page():
        return send_from_directory(app.template_folder, 'propuestas.html')

    @app.route('/alertas')
    def alertas_page():
        return send_from_directory(app.template_folder, 'alertas.html')

    @app.route('/reportes')
    def reportes_page():
        return send_from_directory(app.template_folder, 'reportes.html')

    @app.route('/auditoria')
    def auditoria_page():
        return send_from_directory(app.template_folder, 'auditoria.html')

    @app.route('/perfil')
    def perfil_page():
        return send_from_directory(app.template_folder, 'perfil.html')

    @app.route('/configuracion')
    def configuracion_page():
        return send_from_directory(app.template_folder, 'configuracion.html')

    @app.route('/pausas-activas')
    def pausas_page():
        return send_from_directory(app.template_folder, 'pausas_activas.html')

    @app.route('/blog')
    def blog_page():
        return send_from_directory(app.template_folder, 'blog_articulo.html')

    return app
