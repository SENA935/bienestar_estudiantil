from ..extensions import db


class PreguntaEncuesta(db.Model):
    __tablename__ = 'preguntas_encuesta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    orden = db.Column(db.Integer, default=0)
    requerida = db.Column(db.Boolean, default=True)
    opciones = db.relationship('OpcionPregunta', backref='pregunta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'encuesta_id': self.encuesta_id, 'texto': self.texto,
            'tipo': self.tipo, 'orden': self.orden, 'requerida': self.requerida,
            'opciones': [o.to_dict() for o in self.opciones]
        }
