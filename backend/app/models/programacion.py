from datetime import datetime
from ..extensions import db


class Programacion(db.Model):
    __tablename__ = 'programaciones'

    id = db.Column(db.Integer, primary_key=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_final = db.Column(db.Time, nullable=False)
    lugar = db.Column(db.String(200))
    estado = db.Column(db.String(20), default='Programada')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    docente = db.relationship('Usuario', backref='programaciones_docente', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'actividad_id': self.actividad_id,
            'actividad_titulo': self.actividad.titulo if self.actividad else None,
            'actividad_categoria': self.actividad.categoria if self.actividad else None,
            'curso_id': self.curso_id,
            'curso_nombre': self.curso.nombre if self.curso else None,
            'docente_id': self.docente_id,
            'docente_nombre': f"{self.docente.nombre} {self.docente.apellido}" if self.docente else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_final': self.hora_final.strftime('%H:%M') if self.hora_final else None,
            'lugar': self.lugar,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
