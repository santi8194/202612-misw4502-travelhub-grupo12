from config.db import db

class ReservaDTO(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.String(40), primary_key=True)
    usuario = db.Column(db.String(40), nullable=False)
    id_categoria = db.Column(db.String(40), nullable=False)
    codigo_confirmacion_ota = db.Column(db.String(100), nullable=True)
    codigo_localizador_pms = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(20), nullable=False)
    fecha_check_in = db.Column(db.String(20), nullable=True)
    fecha_check_out = db.Column(db.String(20), nullable=True)
    ocupacion_adultos = db.Column(db.Integer, nullable=True)
    ocupacion_ninos = db.Column(db.Integer, nullable=True)
    ocupacion_infantes = db.Column(db.Integer, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)
