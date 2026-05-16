import uuid

from config.db import db
from modulos.reserva.infraestructura.dto import AuditoriaCancelacionReservaDTO
from modulos.reserva.infraestructura.repositorios import RepositorioAuditoriaCancelacionReserva


def _registrar_inicio(repo, id_reserva: str, reference: str):
    return repo.registrar_inicio_cancelacion(
        id_reserva=id_reserva,
        id_usuario=str(uuid.uuid4()),
        ip_origen=None,
        motivo=None,
        estado_anterior="CONFIRMADA",
        estado_nuevo="CANCELACION_EN_PROCESO",
        politica_tipo="PARTIAL_REFUND",
        dias_anticipacion=2,
        porcentaje_penalidad=50,
        monto_pagado=1000,
        monto_reembolso=500,
        refund_status="PENDING",
        pms_status="PENDING",
        cancellation_reference=reference,
        origen="HU_WEB_11",
    )


def test_repositorio_auditoria_registra_inicio_cancelacion(app):
    id_reserva = str(uuid.uuid4())
    reference = f"CXL-{id_reserva[:8].upper()}"
    repo = RepositorioAuditoriaCancelacionReserva()

    with app.app_context():
        auditoria = _registrar_inicio(repo, id_reserva, reference)
        db.session.commit()

        guardada = db.session.get(AuditoriaCancelacionReservaDTO, auditoria.id)

        assert guardada.id_reserva == id_reserva
        assert guardada.ip_origen is None
        assert guardada.motivo is None
        assert guardada.estado_anterior == "CONFIRMADA"
        assert guardada.estado_nuevo == "CANCELACION_EN_PROCESO"
        assert guardada.politica_tipo == "PARTIAL_REFUND"
        assert guardada.porcentaje_penalidad == 50
        assert guardada.monto_pagado == 1000
        assert guardada.monto_reembolso == 500
        assert guardada.refund_status == "PENDING"
        assert guardada.pms_status == "PENDING"
        assert guardada.cancellation_reference == reference
        assert guardada.origen == "HU_WEB_11"


def test_repositorio_auditoria_registra_confirmacion_pms(app):
    id_reserva = str(uuid.uuid4())
    reference = f"CXL-{id_reserva[:8].upper()}"
    repo = RepositorioAuditoriaCancelacionReserva()

    with app.app_context():
        _registrar_inicio(repo, id_reserva, reference)
        final = repo.registrar_confirmacion_pms(id_reserva=id_reserva)
        db.session.commit()

        guardada = db.session.get(AuditoriaCancelacionReservaDTO, final.id)

        assert guardada.id_reserva == id_reserva
        assert guardada.estado_anterior == "CANCELACION_EN_PROCESO"
        assert guardada.estado_nuevo == "CANCELADA"
        assert guardada.cancellation_reference == reference
        assert guardada.pms_status == "CONFIRMED"
        assert guardada.refund_status == "PENDING"
        assert guardada.origen == "PMS_CANCELLATION_CONFIRMED"


def test_repositorio_auditoria_confirmacion_pms_duplicada_es_idempotente(app):
    id_reserva = str(uuid.uuid4())
    reference = f"CXL-{id_reserva[:8].upper()}"
    repo = RepositorioAuditoriaCancelacionReserva()

    with app.app_context():
        _registrar_inicio(repo, id_reserva, reference)
        primera = repo.registrar_confirmacion_pms(id_reserva=id_reserva)
        segunda = repo.registrar_confirmacion_pms(id_reserva=id_reserva)
        db.session.commit()

        finales = (
            db.session.query(AuditoriaCancelacionReservaDTO)
            .filter_by(
                id_reserva=id_reserva,
                cancellation_reference=reference,
                estado_nuevo="CANCELADA",
            )
            .all()
        )

        assert segunda.id == primera.id
        assert len(finales) == 1
