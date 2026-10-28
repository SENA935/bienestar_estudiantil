from ..extensions import db
from datetime import datetime


class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    estado = db.Column(db.String(20), default='Activo')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'apellido': self.apellido,
            'documento': self.documento, 'curso_id': self.curso_id,
            'curso_nombre': self.curso.nombre if self.curso else None,
            'email': self.email,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
