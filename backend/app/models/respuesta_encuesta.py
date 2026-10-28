from ..extensions import db
from datetime import datetime


class RespuestaEncuesta(db.Model):
    __tablename__ = 'respuestas_encuesta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref='respuestas_encuestas')
    respuestas = db.relationship('RespuestaPregunta', backref='respuesta_encuesta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'encuesta_id': self.encuesta_id, 'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None,
            'fecha_respuesta': self.fecha_respuesta.isoformat() if self.fecha_respuesta else None,
            'respuestas': [r.to_dict() for r in self.respuestas]
        }
