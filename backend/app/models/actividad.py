from datetime import datetime
from ..extensions import db


class Actividad(db.Model):
    __tablename__ = 'actividades'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50), nullable=False)
    duracion = db.Column(db.Integer, default=30)
    instrucciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Activa')
    imagen = db.Column(db.String(256))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    programaciones = db.relationship('Programacion', backref='actividad', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'duracion': self.duracion,
            'instrucciones': self.instrucciones,
            'estado': self.estado,
            'imagen': self.imagen,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
