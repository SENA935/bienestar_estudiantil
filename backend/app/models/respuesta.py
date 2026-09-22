from datetime import datetime
from ..extensions import db


class RespuestaEncuesta(db.Model):
    __tablename__ = 'respuestas_encuesta'

    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='respuestas_encuesta', lazy=True)
    respuestas = db.relationship('RespuestaPregunta', backref='respuesta_encuesta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'encuesta_id': self.encuesta_id,
            'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None,
            'fecha_respuesta': self.fecha_respuesta.isoformat() if self.fecha_respuesta else None,
            'respuestas': [r.to_dict() for r in self.respuestas]
        }


class RespuestaPregunta(db.Model):
    __tablename__ = 'respuestas_pregunta'

    id = db.Column(db.Integer, primary_key=True)
    respuesta_encuesta_id = db.Column(db.Integer, db.ForeignKey('respuestas_encuesta.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_encuesta.id'), nullable=False)
    opcion_id = db.Column(db.Integer, db.ForeignKey('opciones_pregunta.id'))
    texto_respuesta = db.Column(db.Text)
    valor_numerico = db.Column(db.Integer)

    pregunta = db.relationship('PreguntaEncuesta', backref='respuestas_preguntas', lazy=True)
    opcion = db.relationship('OpcionPregunta', backref='seleccionada_en', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'pregunta_id': self.pregunta_id,
            'opcion_id': self.opcion_id,
            'opcion_texto': self.opcion.texto if self.opcion else None,
            'texto_respuesta': self.texto_respuesta,
            'valor_numerico': self.valor_numerico
        }
