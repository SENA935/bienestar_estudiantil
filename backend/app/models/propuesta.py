from datetime import datetime
from ..extensions import db


class Propuesta(db.Model):
    __tablename__ = 'propuestas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='Pendiente')
    observaciones_coordinador = db.Column(db.Text)

    estudiante = db.relationship('Usuario', backref='propuestas', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'estudiante_id': self.estudiante_id,
            'estudiante_nombre': f"{self.estudiante.nombre} {self.estudiante.apellido}" if self.estudiante else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado,
            'observaciones_coordinador': self.observaciones_coordinador
        }
