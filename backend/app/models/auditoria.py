from datetime import datetime
from ..extensions import db


class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    ip = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='auditorias', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else 'Sistema',
            'modulo': self.modulo,
            'accion': self.accion,
            'descripcion': self.descripcion,
            'ip': self.ip,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
