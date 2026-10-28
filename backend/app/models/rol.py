from ..extensions import db


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion}
