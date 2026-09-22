from datetime import datetime
from ..extensions import db


class Institucion(db.Model):
    __tablename__ = 'instituciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    estado = db.Column(db.String(20), default='Activa')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    sedes = db.relationship('Sede', backref='institucion', lazy=True)
    usuarios = db.relationship('Usuario', backref='institucion', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nit': self.nit,
            'telefono': self.telefono,
            'email': self.email,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'sedes_count': len(self.sedes)
        }
