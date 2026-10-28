import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import create_app
from app.extensions import db
import app.models  # noqa: F401  (registra todos los modelos)

app = create_app()


def ensure_database():
    """Crea las tablas y los datos iniciales en el primer arranque."""
    with app.app_context():
        db.create_all()

        from app.models.rol import Rol

        if Rol.query.count() == 0:
            from seed import seed

            seed()


try:
    ensure_database()
except Exception as exc:  # noqa: BLE001
    app.logger.error("No se pudo inicializar la base de datos: %s", exc)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
