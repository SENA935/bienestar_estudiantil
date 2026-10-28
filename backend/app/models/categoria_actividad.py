from ..extensions import db


class CategoriaActividad(db.Model):
    __tablename__ = 'categorias_actividad'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    color = db.Column(db.String(20), default='#087f8c')
    actividades = db.relationship('Actividad', backref='categoria', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion, 'color': self.color}
