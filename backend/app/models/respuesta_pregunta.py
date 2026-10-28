from ..extensions import db


class RespuestaPregunta(db.Model):
    __tablename__ = 'respuestas_pregunta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    respuesta_encuesta_id = db.Column(db.Integer, db.ForeignKey('respuestas_encuesta.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_encuesta.id'), nullable=False)
    opcion_id = db.Column(db.Integer, db.ForeignKey('opciones_pregunta.id'))
    valor_texto = db.Column(db.Text)
    valor_numero = db.Column(db.Float)
    pregunta = db.relationship('PreguntaEncuesta')
    opcion = db.relationship('OpcionPregunta')

    def to_dict(self):
        return {
            'id': self.id, 'pregunta_id': self.pregunta_id,
            'pregunta_texto': self.pregunta.texto if self.pregunta else None,
            'opcion_id': self.opcion_id,
            'opcion_texto': self.opcion.texto if self.opcion else None,
            'valor_texto': self.valor_texto, 'valor_numero': self.valor_numero
        }
