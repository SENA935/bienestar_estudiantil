import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario


def provision():
    app = create_app()
    with app.app_context():
        db.create_all()
        if Usuario.query.count() == 0:
            from seed import seed
            seed()
            print("Seed ejecutado: base de datos poblada")
        else:
            print("La base de datos ya tiene datos, se omitio el seed")


if __name__ == '__main__':
    provision()