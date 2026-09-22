from datetime import datetime
from ..extensions import db


class Encuesta(db.Model):
    __tablename__ = 'encuestas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    preguntas = db.relationship('PreguntaEncuesta', backref='encuesta', lazy=True, cascade='all, delete-orphan')
    respuestas = db.relationship('RespuestaEncuesta', backref='encuesta', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'preguntas_count': len(self.preguntas),
            'respuestas_count': len(self.respuestas)
        }


class PreguntaEncuesta(db.Model):
    __tablename__ = 'preguntas_encuesta'

    id = db.Column(db.Integer, primary_key=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    orden = db.Column(db.Integer, default=0)
    requerida = db.Column(db.Boolean, default=True)

    opciones = db.relationship('OpcionPregunta', backref='pregunta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'encuesta_id': self.encuesta_id,
            'texto': self.texto,
            'tipo': self.tipo,
            'orden': self.orden,
            'requerida': self.requerida,
            'opciones': [o.to_dict() for o in self.opciones]
        }


class OpcionPregunta(db.Model):
    __tablename__ = 'opciones_pregunta'

    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_encuesta.id'), nullable=False)
    texto = db.Column(db.String(300), nullable=False)
    valor = db.Column(db.Integer, default=0)
    orden = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'pregunta_id': self.pregunta_id,
            'texto': self.texto,
            'valor': self.valor,
            'orden': self.orden
        }
