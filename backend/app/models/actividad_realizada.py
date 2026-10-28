from ..extensions import db
from datetime import datetime


class ActividadRealizada(db.Model):
    __tablename__ = 'actividades_realizadas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    programacion_id = db.Column(db.Integer, db.ForeignKey('programaciones.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)
    hora_final = db.Column(db.Time)
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Realizada')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        p = self.programacion
        return {
            'id': self.id, 'programacion_id': self.programacion_id,
            'actividad_titulo': p.actividad.titulo if p and p.actividad else None,
            'curso_nombre': p.curso.nombre if p and p.curso else None,
            'docente_nombre': f"{p.docente.nombre} {p.docente.apellido}" if p and p.docente else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_final': self.hora_final.strftime('%H:%M') if self.hora_final else None,
            'observaciones': self.observaciones, 'estado': self.estado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
