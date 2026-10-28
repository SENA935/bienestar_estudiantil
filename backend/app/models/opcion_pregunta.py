from ..extensions import db


class OpcionPregunta(db.Model):
    __tablename__ = 'opciones_pregunta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_encuesta.id'), nullable=False)
    texto = db.Column(db.String(300), nullable=False)
    valor = db.Column(db.Integer)
    orden = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'id': self.id, 'pregunta_id': self.pregunta_id, 'texto': self.texto, 'valor': self.valor, 'orden': self.orden}
