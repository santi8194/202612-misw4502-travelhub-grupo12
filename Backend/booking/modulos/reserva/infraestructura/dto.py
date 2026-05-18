from config.db import db

class ReservaDTO(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.String(40), primary_key=True)
    usuario = db.Column(db.String(40), nullable=False)
    usuario_email = db.Column(db.String(255), nullable=True)
    id_categoria = db.Column(db.String(40), nullable=False)
    codigo_confirmacion_ota = db.Column(db.String(100), nullable=True)
    codigo_localizador_pms = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(30), nullable=False)
    fecha_check_in = db.Column(db.String(20), nullable=True)
    fecha_check_out = db.Column(db.String(20), nullable=True)
    ocupacion_adultos = db.Column(db.Integer, nullable=True)
    ocupacion_ninos = db.Column(db.Integer, nullable=True)
    ocupacion_infantes = db.Column(db.Integer, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)


class AuditoriaCancelacionReservaDTO(db.Model):
    __tablename__ = "auditoria_cancelacion_reserva"

    id = db.Column(db.String(40), primary_key=True)
    id_reserva = db.Column(db.String(40), nullable=False, index=True)
    id_usuario = db.Column(db.String(40), nullable=True)
    ip_origen = db.Column(db.String(45), nullable=True)
    motivo = db.Column(db.Text, nullable=True)
    estado_anterior = db.Column(db.String(30), nullable=False)
    estado_nuevo = db.Column(db.String(30), nullable=False)
    politica_tipo = db.Column(db.String(40), nullable=True)
    dias_anticipacion = db.Column(db.Integer, nullable=True)
    porcentaje_penalidad = db.Column(db.Float, nullable=True)
    monto_pagado = db.Column(db.Float, nullable=True)
    monto_reembolso = db.Column(db.Float, nullable=True)
    refund_status = db.Column(db.String(30), nullable=True)
    pms_status = db.Column(db.String(30), nullable=True)
    cancellation_reference = db.Column(db.String(80), nullable=False, index=True)
    origen = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
