from ..extensions import db
from datetime import datetime


class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    grado = db.Column(db.String(20), nullable=False)
    jornada = db.Column(db.String(30), default='Mañana')
    director_grupo = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='Activo')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estudiantes = db.relationship('Estudiante', backref='curso', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'grado': self.grado,
            'jornada': self.jornada, 'director_grupo': self.director_grupo,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'estudiantes_count': len(self.estudiantes)
        }
