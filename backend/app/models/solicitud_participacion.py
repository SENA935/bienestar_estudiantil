from ..extensions import db
from datetime import datetime


class SolicitudParticipacion(db.Model):
    __tablename__ = 'solicitudes_participacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    programacion_id = db.Column(db.Integer, db.ForeignKey('programaciones.id'), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.String(20), default='Pendiente')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    estudiante = db.relationship('Usuario', foreign_keys=[estudiante_id], backref='solicitudes_participacion')
    actividad = db.relationship('Actividad', backref='solicitudes')
    programacion = db.relationship('Programacion', backref='solicitudes')
    docente = db.relationship('Usuario', foreign_keys=[docente_id], backref='solicitudes_recibidas')

    def to_dict(self):
        return {
            'id': self.id,
            'estudiante_id': self.estudiante_id,
            'estudiante_nombre': f"{self.estudiante.nombre} {self.estudiante.apellido}" if self.estudiante else None,
            'estudiante_doc': self.estudiante.documento if self.estudiante else None,
            'actividad_id': self.actividad_id,
            'actividad_titulo': self.actividad.titulo if self.actividad else None,
            'programacion_id': self.programacion_id,
            'curso_nombre': self.programacion.curso.nombre if self.programacion and self.programacion.curso else None,
            'docente_id': self.docente_id,
            'docente_nombre': f"{self.docente.nombre} {self.docente.apellido}" if self.docente else None,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
