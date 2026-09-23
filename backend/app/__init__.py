from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(
        __name__,
        template_folder='../../frontend/templates',
        static_folder='../../frontend/static'
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    from .models import usuario, rol, institucion, sede, curso, estudiante
    from .models import actividad, programacion, encuesta, respuesta, propuesta
    from .models import alerta, auditoria, periodo_academico, categoria_actividad

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.usuarios import usuarios_bp
    from .routes.instituciones import instituciones_bp
    from .routes.cursos import cursos_bp
    from .routes.actividades import actividades_bp
    from .routes.encuestas import encuestas_bp
    from .routes.propuestas import propuestas_bp
    from .routes.reportes import reportes_bp
    from .routes.alertas import alertas_bp
    from .routes.auditoria import auditoria_bp
    from .routes.perfil import perfil_bp
    from .routes.configuracion import configuracion_bp
    from .routes.programaciones import programaciones_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(instituciones_bp, url_prefix='/api/instituciones')
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    app.register_blueprint(actividades_bp, url_prefix='/api/actividades')
    app.register_blueprint(encuestas_bp, url_prefix='/api/encuestas')
    app.register_blueprint(propuestas_bp, url_prefix='/api/propuestas')
    app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    app.register_blueprint(alertas_bp, url_prefix='/api/alertas')
    app.register_blueprint(auditoria_bp, url_prefix='/api/auditoria')
    app.register_blueprint(perfil_bp, url_prefix='/api/perfil')
    app.register_blueprint(configuracion_bp, url_prefix='/api/configuracion')
    app.register_blueprint(programaciones_bp, url_prefix='/api/programaciones')

    from .routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    _auto_provision(app)

    return app


def _auto_provision(app):
    with app.app_context():
        try:
            from .extensions import db
            db.create_all()
            from ..seed import seed
            seed(app)
        except Exception as e:
            app.logger.warning('Auto-provision no completo: %s', e)
