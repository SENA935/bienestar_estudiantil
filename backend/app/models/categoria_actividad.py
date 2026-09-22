from datetime import datetime
from ..extensions import db


class CategoriaActividad(db.Model):
    __tablename__ = 'categorias_actividad'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(20), default='#3B82F6')
    estado = db.Column(db.String(20), default='Activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
