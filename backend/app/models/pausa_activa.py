from ..extensions import db
from datetime import datetime


class PausaActiva(db.Model):
    __tablename__ = 'pausas_activas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    instrucciones = db.Column(db.Text)
    duracion_segundos = db.Column(db.Integer, default=180)
    dificultad = db.Column(db.String(20), default='Facil')
    color = db.Column(db.String(20), default='#087f8c')
    bg_gradient = db.Column(db.String(200), default='linear-gradient(135deg,#dcfce7,#a5f3fc)')
    icono = db.Column(db.String(50), default='fa-heart')
    video_url = db.Column(db.String(500))
    estado = db.Column(db.String(20), default='Activa')
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    autor = db.relationship('Usuario', backref='pausas_creadas')

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion,
            'instrucciones': self.instrucciones, 'duracion_segundos': self.duracion_segundos,
            'dificultad': self.dificultad, 'color': self.color,
            'bg_gradient': self.bg_gradient, 'icono': self.icono,
            'video_url': self.video_url, 'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
