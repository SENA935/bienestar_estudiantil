from ..extensions import db
from datetime import datetime


class Encuesta(db.Model):
    __tablename__ = 'encuestas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    preguntas = db.relationship('PreguntaEncuesta', backref='encuesta', lazy=True, cascade='all, delete-orphan')
    respuestas = db.relationship('RespuestaEncuesta', backref='encuesta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'titulo': self.titulo, 'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'preguntas_count': len(self.preguntas), 'respuestas_count': len(self.respuestas)
        }
