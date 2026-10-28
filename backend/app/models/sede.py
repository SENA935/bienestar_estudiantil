from ..extensions import db


class Sede(db.Model):
    __tablename__ = 'sedes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(300))
    institucion_id = db.Column(db.Integer, db.ForeignKey('instituciones.id'), nullable=False)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activa')

    def to_dict(self):
        return {
            'id': self.id, 'nombre': self.nombre, 'direccion': self.direccion,
            'institucion_id': self.institucion_id,
            'institucion_nombre': self.institucion.nombre if self.institucion else None,
            'telefono': self.telefono, 'estado': self.estado
        }
