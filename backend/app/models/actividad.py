from ..extensions import db
from datetime import datetime


class Actividad(db.Model):
    __tablename__ = 'actividades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_actividad.id'), nullable=False)
    duracion = db.Column(db.Integer, default=30)
    instrucciones = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='Activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    programaciones = db.relationship('Programacion', backref='actividad', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'titulo': self.titulo, 'descripcion': self.descripcion,
            'categoria_id': self.categoria_id,
            'categoria_nombre': self.categoria.nombre if self.categoria else None,
            'duracion': self.duracion, 'instrucciones': self.instrucciones,
            'imagen': self.imagen, 'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
