import uuid
import datetime
from unittest.mock import MagicMock
from types import SimpleNamespace

import pytest
import modulos.reserva.infraestructura.api as reserva_api_mod
from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient


@pytest.fixture(autouse=True)
def stub_catalog_client(monkeypatch):
    monkeypatch.setattr(CatalogServiceClient, 'reserve_inventory', lambda self, id_categoria, fecha_check_in, fecha_check_out: [])
    monkeypatch.setattr(CatalogServiceClient, 'restore_inventory', lambda self, id_categoria, original_items: None)

def test_healthcheck(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.is_json
    assert response.json == {'status': 'healthy', 'service': 'booking'}


def test_create_reserva_hold_returns_201_and_id(client):
    payload = {
        'id_usuario': str(uuid.uuid4()),
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {
            'adultos': 2,
            'ninos': 1,
            'infantes': 0
        }
    }

    response = client.post('/api/reserva', json=payload)

    assert response.status_code == 201
    assert response.is_json
    body = response.json
    assert 'id_reserva' in body
    assert body['mensaje'] == 'Reserva creada en estado HOLD'
    assert uuid.UUID(body['id_reserva'])


def test_create_reserva_hold_missing_required_field_returns_400(client):
    payload = {
        'id_usuario': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {
            'adultos': 1,
            'ninos': 0,
            'infantes': 0
        }
    }

    response = client.post('/api/reserva', json=payload)

    assert response.status_code == 400
    assert response.is_json
    body = response.json
    assert 'error' in body
    assert "id_categoria" in body['error'] or "id_categoria" in body['error'].lower()

def test_create_reserva_hold_invalid_uuid_returns_400(client):
    payload = {
        'id_usuario': 'invalid-uuid',
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {
            'adultos': 1,
            'ninos': 0,
            'infantes': 0
        }
    }

    response = client.post('/api/reserva', json=payload)

    assert response.status_code == 400
    assert response.is_json
    body = response.json
    assert 'error' in body
    assert "badly formed hexadecimal UUID" in body['error'] or "badly formed hexadecimal UUID" in body['error'].lower()


def test_create_reserva_hold_no_payload_returns_400(client):
    response = client.post('/api/reserva', json={})

    assert response.status_code == 400
    assert response.is_json
    assert "No data provided" in response.json["error"]


def test_create_reserva_hold_categoria_no_existe_returns_400(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            raise ValueError("La categoria no existe en catalog")

    monkeypatch.setattr(reserva_api_mod, 'CrearReservaHoldHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    payload = {
        'id_usuario': str(uuid.uuid4()),
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {'adultos': 2, 'ninos': 0, 'infantes': 0}
    }

    response = client.post('/api/reserva', json=payload)

    assert response.status_code == 400
    assert 'categoria no existe' in response.json['error']


def test_create_reserva_hold_sin_disponibilidad_returns_400(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            raise ValueError("No hay disponibilidad para la categoria en la fecha 2026-04-01")

    monkeypatch.setattr(reserva_api_mod, 'CrearReservaHoldHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    payload = {
        'id_usuario': str(uuid.uuid4()),
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {'adultos': 2, 'ninos': 0, 'infantes': 0}
    }

    response = client.post('/api/reserva', json=payload)

    assert response.status_code == 400
    assert 'No hay disponibilidad' in response.json['error']

def test_formalizar_reserva_returns_200_when_handler_ok(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            return True

    monkeypatch.setattr(reserva_api_mod, 'FormalizarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/formalizar')

    assert response.status_code == 200
    assert response.is_json
    assert "Reserva formalizada" in response.json["mensaje"]


def test_formalizar_reserva_con_intencion_pago_devuelve_checkout(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            assert comando.monto == 120000
            assert comando.moneda == "COP"
            return True

    checkout = {
        "id_pago": "pay-1",
        "id_reserva": "reserva-1",
        "estado": "PENDING",
        "checkout": {
            "public_key": "pub_test",
            "reference": "PAY-1",
            "amount_in_cents": 12000000,
            "currency": "COP",
            "signature_integrity": "sig"
        }
    }

    monkeypatch.setattr(reserva_api_mod, 'FormalizarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'crear_checkout_pago', lambda *_args: checkout)

    id_reserva = str(uuid.uuid4())
    response = client.post(
        f'/api/reserva/{id_reserva}/formalizar',
        json={"intencion_pago": {"monto": 120000, "moneda": "COP"}}
    )

    assert response.status_code == 200
    assert response.json["id_reserva"] == id_reserva
    assert response.json["pago"]["checkout"]["reference"] == "PAY-1"


def test_formalizar_reserva_invalid_uuid_returns_400(client):
    response = client.post('/api/reserva/uuid-invalido/formalizar')

    assert response.status_code == 400
    assert response.is_json
    assert "badly formed hexadecimal UUID" in response.json["error"]


def test_formalizar_reserva_handler_value_error_returns_400(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            raise ValueError("No se encontró la reserva")

    monkeypatch.setattr(reserva_api_mod, 'FormalizarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/formalizar')

    assert response.status_code == 400
    assert response.is_json
    assert "No se encontró la reserva" in response.json["error"]


def test_formalizar_reserva_unexpected_error_returns_500(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            raise RuntimeError("Error inesperado")

    monkeypatch.setattr(reserva_api_mod, 'FormalizarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/formalizar')

    assert response.status_code == 500
    assert response.is_json
    assert "Error inesperado" in response.json["error"]


def test_expirar_reserva_returns_200_when_handler_ok(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            return True

    monkeypatch.setattr(reserva_api_mod, 'ExpirarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/expirar')

    assert response.status_code == 200
    assert response.is_json
    assert response.json["mensaje"] == "Reserva marcada como EXPIRADA"


def test_expirar_reserva_invalid_uuid_returns_400(client):
    response = client.post('/api/reserva/uuid-invalido/expirar')

    assert response.status_code == 400
    assert response.is_json
    assert "badly formed hexadecimal UUID" in response.json["error"]


def test_expirar_reserva_handler_value_error_returns_400(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, comando):
            raise ValueError("La reserva debe estar en HOLD para marcarse como EXPIRADA")

    monkeypatch.setattr(reserva_api_mod, 'ExpirarReservaHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/expirar')

    assert response.status_code == 400
    assert response.is_json
    assert "EXPIRADA" in response.json["error"]


def test_cancelar_reserva_sin_body_rechaza_bypass_legacy(client):
    id_reserva = str(uuid.uuid4())
    response = client.post(f'/api/reserva/{id_reserva}/cancelar')

    assert response.status_code == 400
    assert response.is_json
    assert "terminos" in response.json["error"]


def test_cancelar_reserva_invalid_uuid_returns_400(client):
    response = client.post(
        '/api/reserva/uuid-invalido/cancelar',
        json={"acceptedTerms": True},
        headers={"Authorization": f"Bearer user:{uuid.uuid4()}"},
    )

    assert response.status_code == 400
    assert response.is_json
    assert "badly formed hexadecimal UUID" in response.json["error"]


def test_cancelar_reserva_con_accepted_terms_inicia_cancelacion_controlada(client, monkeypatch):
    reserva = _fake_reserva_preview()
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=50)
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True, "reason": "Cambio de planes"},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 200
    body = response.json
    assert body["reservationId"] == str(reserva.id)
    assert body["reservationStatus"] == "CANCELACION_EN_PROCESO"
    assert body["cancellationReference"] == f"CXL-{str(reserva.id)[:8].upper()}"
    assert body["refundAmount"] == 500
    assert body["refundStatus"] == "PENDING"
    assert body["processingTimeLabel"] == "5 a 10 dias habiles"
    assert body["pmsStatus"] == "PENDING"
    assert body["mensaje"] == "Cancelacion iniciada correctamente"
    assert reserva.estado.value == "CANCELACION_EN_PROCESO"
    assert len(auditorias) == 1
    auditoria = auditorias[0]
    assert auditoria["id_reserva"] == str(reserva.id)
    assert auditoria["id_usuario"] == str(reserva.usuario.id)
    assert auditoria["motivo"] == "Cambio de planes"
    assert auditoria["estado_anterior"] == "CONFIRMADA"
    assert auditoria["estado_nuevo"] == "CANCELACION_EN_PROCESO"
    assert auditoria["politica_tipo"] == "PARTIAL_REFUND"
    assert auditoria["dias_anticipacion"] == 2
    assert auditoria["porcentaje_penalidad"] == 50
    assert auditoria["monto_pagado"] == 1000
    assert auditoria["monto_reembolso"] == 500
    assert auditoria["refund_status"] == "PENDING"
    assert auditoria["pms_status"] == "PENDING"
    assert auditoria["cancellation_reference"] == body["cancellationReference"]
    assert auditoria["origen"] == "HU_WEB_11"


def test_cancelar_reserva_con_accepted_terms_emite_comando_pms(client, monkeypatch):
    reserva = _fake_reserva_preview()
    uows = []

    def uow_factory():
        uow = MagicMock()
        uow.__enter__ = MagicMock(return_value=uow)
        uow.__exit__ = MagicMock(return_value=None)
        uows.append(uow)
        return uow

    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=50)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', uow_factory)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 200
    pms_commands = [
        command
        for uow in uows
        for call in uow.agregar_eventos.call_args_list
        for command in call.args[0]
        if command.__class__.__name__ == "CancelarReservaPmsCmd"
    ]
    assert len(pms_commands) == 1
    assert pms_commands[0].id_reserva == reserva.id
    assert pms_commands[0].id_categoria == reserva.id_categoria


def test_cancelar_reserva_con_reason_vacio_lo_acepta_como_no_informado(client, monkeypatch):
    reserva = _fake_reserva_preview()
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=0)
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True, "reason": "   "},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 200
    assert response.json["reservationStatus"] == "CANCELACION_EN_PROCESO"
    assert auditorias[0]["motivo"] is None


def test_cancelar_reserva_sin_reembolso_devuelve_processing_time_null(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=100)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 200
    assert response.json["refundAmount"] == 0
    assert response.json["refundStatus"] == "NOT_APPLICABLE"
    assert response.json["processingTimeLabel"] is None


@pytest.mark.parametrize("payload", [{"acceptedTerms": False}, {"acceptedTerms": None}, {}])
def test_cancelar_reserva_con_accepted_terms_invalido_returns_400(client, payload):
    response = client.post(f'/api/reserva/{uuid.uuid4()}/cancelar', json=payload)

    assert response.status_code == 400
    assert response.is_json
    assert "terminos" in response.json["error"]


def test_cancelar_reserva_con_accepted_terms_invalido_no_crea_auditoria(client, monkeypatch):
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{uuid.uuid4()}/cancelar',
        json={"acceptedTerms": False},
    )

    assert response.status_code == 400
    assert auditorias == []


def test_cancelar_reserva_rechaza_usuario_no_dueno_sin_pms_ni_auditoria(client, monkeypatch):
    reserva = _fake_reserva_preview()
    uows = []
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    def uow_factory():
        uow = MagicMock()
        uow.__enter__ = MagicMock(return_value=uow)
        uow.__exit__ = MagicMock(return_value=None)
        uows.append(uow)
        return uow

    _setup_cancelacion_preview(monkeypatch, reserva)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', uow_factory)
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers={"Authorization": f"Bearer user:{uuid.uuid4()}"},
    )

    assert response.status_code == 403
    assert "permiso" in response.json["error"]
    assert all(not uow.agregar_eventos.called for uow in uows)
    assert auditorias == []


def test_cancelar_reserva_hu_web_11_not_found_returns_404(client, monkeypatch):
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, _reserva_id):
            return None

    monkeypatch.setattr(reserva_api_mod, 'ObtenerReservaPorIdHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{uuid.uuid4()}/cancelar',
        json={"acceptedTerms": True},
        headers={"Authorization": f"Bearer user:{uuid.uuid4()}"},
    )

    assert response.status_code == 404
    assert response.is_json
    assert "No se encontro la reserva" in response.json["error"]
    assert auditorias == []


@pytest.mark.parametrize("estado", ["HOLD", "CANCELADA", "EXPIRADA", "PENDIENTE", "CANCELACION_EN_PROCESO"])
def test_cancelar_reserva_hu_web_11_estado_no_cancelable_returns_400(client, monkeypatch, estado):
    reserva = _fake_reserva_preview(estado=estado)
    _setup_cancelacion_preview(monkeypatch, reserva)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 400
    assert response.is_json
    assert response.json["reservationId"] == str(reserva.id)
    assert response.json["reservationStatus"] == estado
    assert response.json["cancellationReference"] == f"CXL-{str(reserva.id)[:8].upper()}"
    assert "error" in response.json


def test_cancelar_reserva_hu_web_11_no_emite_pms_si_no_es_cancelable(client, monkeypatch):
    reserva = _fake_reserva_preview(estado="CANCELADA")
    uows = []
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    def uow_factory():
        uow = MagicMock()
        uow.__enter__ = MagicMock(return_value=uow)
        uow.__exit__ = MagicMock(return_value=None)
        uows.append(uow)
        return uow

    _setup_cancelacion_preview(monkeypatch, reserva)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', uow_factory)
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 400
    assert all(not uow.agregar_eventos.called for uow in uows)
    assert auditorias == []


def test_cancelar_reserva_en_proceso_no_duplica_pms_ni_auditoria(client, monkeypatch):
    reserva = _fake_reserva_preview(estado="CANCELACION_EN_PROCESO")
    uows = []
    auditorias = []

    class DummyAuditRepo:
        def registrar_inicio_cancelacion(self, **kwargs):
            auditorias.append(kwargs)

    def uow_factory():
        uow = MagicMock()
        uow.__enter__ = MagicMock(return_value=uow)
        uow.__exit__ = MagicMock(return_value=None)
        uows.append(uow)
        return uow

    _setup_cancelacion_preview(monkeypatch, reserva)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', uow_factory)
    monkeypatch.setattr(reserva_api_mod, 'RepositorioAuditoriaCancelacionReserva', DummyAuditRepo)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 400
    assert response.json["reservationStatus"] == "CANCELACION_EN_PROCESO"
    assert all(not uow.agregar_eventos.called for uow in uows)
    assert auditorias == []


def test_cancelar_reserva_hu_web_11_no_invoca_refund_payment(client, monkeypatch):
    reserva = _fake_reserva_preview()
    payment_calls = []

    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, _reserva_id):
            return reserva

    class DummyCatalogClient:
        def get_category_by_id(self, _id_categoria):
            return {
                "politica_cancelacion": {
                    "dias_anticipacion": 2,
                    "porcentaje_penalidad": 50,
                },
            }

        def get_property_by_category_id(self, _id_categoria):
            return {"nombre": "Hotel Andino"}

    class ReadOnlyPaymentClient:
        def get_payment_for_reserva(self, id_reserva):
            payment_calls.append(id_reserva)
            return {"estado": "APPROVED", "monto": 1000, "moneda": "COP"}

    class DummyAuthClient:
        def get_current_user(self, _authorization_header):
            return {"id_usuario": str(reserva.usuario.id)}

    monkeypatch.setattr(reserva_api_mod, 'ObtenerReservaPorIdHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'CatalogServiceClient', DummyCatalogClient)
    monkeypatch.setattr(reserva_api_mod, 'PaymentServiceClient', ReadOnlyPaymentClient)
    monkeypatch.setattr(reserva_api_mod, 'AuthServiceClient', DummyAuthClient)

    response = client.post(
        f'/api/reserva/{reserva.id}/cancelar',
        json={"acceptedTerms": True},
        headers=_owner_headers(reserva),
    )

    assert response.status_code == 200
    assert payment_calls == [str(reserva.id)]


def _fake_reserva_preview(estado='CONFIRMADA', check_in_days=10):
    reserva_id = uuid.uuid4()
    id_categoria = uuid.uuid4()
    reserva = SimpleNamespace(
        id=reserva_id,
        usuario=SimpleNamespace(id=uuid.uuid4()),
        id_categoria=id_categoria,
        codigo_confirmacion_ota='BK-001',
        codigo_localizador_pms=None,
        estado=SimpleNamespace(value=estado),
        fecha_check_in=datetime.date.today() + datetime.timedelta(days=check_in_days),
        fecha_check_out=datetime.date.today() + datetime.timedelta(days=check_in_days + 3),
        ocupacion=SimpleNamespace(adultos=2, ninos=1, infantes=0),
    )

    def iniciar_cancelacion():
        if reserva.estado.value != "CONFIRMADA":
            raise ValueError("La reserva debe estar en CONFIRMADA para iniciar cancelacion")
        reserva.estado = SimpleNamespace(value="CANCELACION_EN_PROCESO")

    reserva.iniciar_cancelacion = iniciar_cancelacion
    return reserva


def _owner_headers(reserva) -> dict:
    return {"Authorization": f"Bearer user:{reserva.usuario.id}"}


def _setup_cancelacion_preview(
    monkeypatch,
    reserva,
    *,
    porcentaje_penalidad=50,
    dias_anticipacion=2,
    payment=None,
):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, reserva_id):
            return reserva

    class DummyCatalogClient:
        def get_category_by_id(self, id_categoria):
            assert id_categoria == str(reserva.id_categoria)
            return {
                "nombre_comercial": "Suite Deluxe",
                "precio_base": {"monto": 120000, "moneda": "COP"},
                "politica_cancelacion": {
                    "dias_anticipacion": dias_anticipacion,
                    "porcentaje_penalidad": porcentaje_penalidad,
                },
            }

        def get_property_by_category_id(self, id_categoria):
            assert id_categoria == str(reserva.id_categoria)
            return {
                "nombre": "Hotel Andino",
                "ubicacion": {"ciudad": "Bogota", "pais": "Colombia"},
            }

    class DummyPaymentClient:
        def get_payment_for_reserva(self, id_reserva):
            assert id_reserva == str(reserva.id)
            return payment or {"estado": "APPROVED", "monto": 1000, "moneda": "COP"}

    class DummyAuthClient:
        def get_current_user(self, authorization_header):
            if not authorization_header or not authorization_header.startswith("Bearer user:"):
                return None
            return {"id_usuario": authorization_header.removeprefix("Bearer user:")}

    monkeypatch.setattr(reserva_api_mod, 'ObtenerReservaPorIdHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'CatalogServiceClient', DummyCatalogClient)
    monkeypatch.setattr(reserva_api_mod, 'PaymentServiceClient', DummyPaymentClient)
    monkeypatch.setattr(reserva_api_mod, 'AuthServiceClient', DummyAuthClient)


def test_cancelacion_preview_confirmada_returns_200(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=50)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["reservationId"] == str(reserva.id)
    assert body["reservationNumber"] == "BK-001"
    assert body["hotelName"] == "Hotel Andino"
    assert body["location"] == "Bogota, Colombia"
    assert body["checkInDate"] == reserva.fecha_check_in.isoformat()
    assert body["checkOutDate"] == reserva.fecha_check_out.isoformat()
    assert body["guests"] == 3
    assert body["currentStatus"] == "CONFIRMADA"
    assert body["totalPaid"] == 1000
    assert body["currency"] == "COP"
    assert body["canCancel"] is True
    assert body["nonCancelableReason"] is None


def test_cancelacion_preview_rechaza_usuario_no_dueno(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva)

    response = client.get(
        f'/api/reserva/{reserva.id}/cancelacion-preview',
        headers={"Authorization": f"Bearer user:{uuid.uuid4()}"},
    )

    assert response.status_code == 403
    assert "permiso" in response.json["error"]


def test_cancelacion_preview_acepta_username_cognito_como_dueno(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva)

    class DummyAuthClient:
        def get_current_user(self, _authorization_header):
            return {
                "id_usuario": str(uuid.uuid4()),
                "username": str(reserva.usuario.id),
            }

    monkeypatch.setattr(reserva_api_mod, 'AuthServiceClient', DummyAuthClient)

    response = client.get(
        f'/api/reserva/{reserva.id}/cancelacion-preview',
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json["reservationId"] == str(reserva.id)


def test_cancelacion_preview_rechaza_solicitud_sin_sesion_autenticada(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview')

    assert response.status_code == 401
    assert "usuario autenticado" in response.json["error"]


def test_cancelacion_preview_not_found_returns_404(client, monkeypatch):
    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, _reserva_id):
            return None

    monkeypatch.setattr(reserva_api_mod, 'ObtenerReservaPorIdHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())

    response = client.get(
        f'/api/reserva/{uuid.uuid4()}/cancelacion-preview',
        headers={"Authorization": f"Bearer user:{uuid.uuid4()}"},
    )

    assert response.status_code == 404
    assert response.is_json
    assert "No se encontro la reserva" in response.json["error"]


@pytest.mark.parametrize(
    "estado, reason_fragment",
    [
        ("CANCELADA", "cancelada"),
        ("EXPIRADA", "expirada"),
        ("HOLD", "HOLD"),
        ("PENDIENTE", "pendiente"),
        ("CANCELACION_EN_PROCESO", "proceso"),
    ],
)
def test_cancelacion_preview_estados_no_cancelables(client, monkeypatch, estado, reason_fragment):
    reserva = _fake_reserva_preview(estado=estado)
    _setup_cancelacion_preview(monkeypatch, reserva)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["currentStatus"] == estado
    assert body["canCancel"] is False
    assert reason_fragment in body["nonCancelableReason"]
    assert body["refund"]["expectedRefundAmount"] == 0
    assert body["refund"]["refundStatus"] == "NOT_APPLICABLE"
    if estado == "CANCELACION_EN_PROCESO":
        assert body["pmsStatus"] == "PENDING"
        assert "proceso" in body["mensaje"]


@pytest.mark.parametrize(
    "porcentaje_penalidad, expected_type, expected_refund, expected_status",
    [
        (0, "FREE_CANCELLATION", 1000, "PENDING"),
        (50, "PARTIAL_REFUND", 500, "PENDING"),
        (100, "NON_REFUNDABLE", 0, "NOT_APPLICABLE"),
    ],
)
def test_cancelacion_preview_politica_y_reembolso(
    client,
    monkeypatch,
    porcentaje_penalidad,
    expected_type,
    expected_refund,
    expected_status,
):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(monkeypatch, reserva, porcentaje_penalidad=porcentaje_penalidad)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["cancellationPolicy"]["type"] == expected_type
    assert body["cancellationPolicy"]["porcentajePenalidad"] == porcentaje_penalidad
    assert body["refund"]["paidAmount"] == 1000
    assert body["refund"]["expectedRefundAmount"] == expected_refund
    assert body["refund"]["refundStatus"] == expected_status


def test_cancelacion_preview_fuera_de_ventana_no_cancelable(client, monkeypatch):
    reserva = _fake_reserva_preview(check_in_days=1)
    _setup_cancelacion_preview(monkeypatch, reserva, dias_anticipacion=2)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["canCancel"] is False
    assert "2 dias de anticipacion" in body["nonCancelableReason"]
    assert body["refund"]["expectedRefundAmount"] == 0
    assert body["refund"]["refundStatus"] == "NOT_APPLICABLE"


def test_cancelacion_preview_reserva_pasada_usa_mensaje_de_estado_actual(client, monkeypatch):
    reserva = _fake_reserva_preview(check_in_days=-1)
    _setup_cancelacion_preview(monkeypatch, reserva, dias_anticipacion=2)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["canCancel"] is False
    assert body["nonCancelableReason"] == "Esta reserva no se puede cancelar por su estado actual."
    assert body["refund"]["expectedRefundAmount"] == 0
    assert body["refund"]["refundStatus"] == "NOT_APPLICABLE"


def test_cancelacion_preview_sin_pago_aprobado_no_cancelable(client, monkeypatch):
    reserva = _fake_reserva_preview()
    _setup_cancelacion_preview(
        monkeypatch,
        reserva,
        payment={"estado": "PENDING", "monto": 1000, "moneda": "COP"},
    )

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    body = response.json
    assert body["canCancel"] is False
    assert "pago aprobado" in body["nonCancelableReason"]
    assert body["totalPaid"] == 1000
    assert body["refund"]["refundStatus"] == "NOT_APPLICABLE"


def test_cancelacion_preview_no_invoca_pms_ni_refund_payment(client, monkeypatch):
    reserva = _fake_reserva_preview()
    payment_calls = []

    class DummyHandler:
        def __init__(self, repositorio, uow):
            self.repositorio = repositorio
            self.uow = uow

        def handle(self, _reserva_id):
            return reserva

    class DummyCatalogClient:
        def get_category_by_id(self, _id_categoria):
            return {
                "politica_cancelacion": {
                    "dias_anticipacion": 2,
                    "porcentaje_penalidad": 0,
                },
            }

        def get_property_by_category_id(self, _id_categoria):
            return {"nombre": "Hotel Andino"}

    class ReadOnlyPaymentClient:
        def get_payment_for_reserva(self, id_reserva):
            payment_calls.append(id_reserva)
            return {"estado": "APPROVED", "monto": 1000, "moneda": "COP"}

    class DummyAuthClient:
        def get_current_user(self, _authorization_header):
            return {"id_usuario": str(reserva.usuario.id)}

    monkeypatch.setattr(reserva_api_mod, 'ObtenerReservaPorIdHandler', DummyHandler)
    monkeypatch.setattr(reserva_api_mod, 'UnidadTrabajoHibrida', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'RepositorioReservas', lambda: MagicMock())
    monkeypatch.setattr(reserva_api_mod, 'CatalogServiceClient', DummyCatalogClient)
    monkeypatch.setattr(reserva_api_mod, 'PaymentServiceClient', ReadOnlyPaymentClient)
    monkeypatch.setattr(reserva_api_mod, 'AuthServiceClient', DummyAuthClient)

    response = client.get(f'/api/reserva/{reserva.id}/cancelacion-preview', headers=_owner_headers(reserva))

    assert response.status_code == 200
    assert payment_calls == [str(reserva.id)]


def test_get_reserva_by_id_returns_200(client):
    payload = {
        'id_usuario': str(uuid.uuid4()),
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {
            'adultos': 2,
            'ninos': 1,
            'infantes': 0
        }
    }

    create_response = client.post('/api/reserva', json=payload)
    assert create_response.status_code == 201
    id_reserva = create_response.json['id_reserva']

    get_response = client.get(f'/api/reserva/{id_reserva}')

    assert get_response.status_code == 200
    assert get_response.is_json
    body = get_response.json
    assert body['id_reserva'] == id_reserva
    assert body['id_categoria'] == payload['id_categoria']
    assert body['fecha_check_in'] == payload['fecha_check_in']
    assert body['fecha_check_out'] == payload['fecha_check_out']


def test_get_reserva_by_id_not_found_returns_404(client):
    response = client.get(f'/api/reserva/{uuid.uuid4()}')

    assert response.status_code == 404
    assert response.is_json
    assert 'No se encontró la reserva' in response.json['error']


def test_get_reserva_by_id_invalid_uuid_returns_400(client):
    response = client.get('/api/reserva/uuid-invalido')

    assert response.status_code == 400
    assert response.is_json
    assert 'badly formed hexadecimal UUID' in response.json['error']


# --- Tests: GET /api/reserva/usuario/<id_usuario> ---

def _payload_reserva(id_usuario: str) -> dict:
    return {
        'id_usuario': id_usuario,
        'id_categoria': str(uuid.uuid4()),
        'fecha_check_in': '2026-04-01',
        'fecha_check_out': '2026-04-05',
        'ocupacion': {'adultos': 2, 'ninos': 0, 'infantes': 0}
    }


def test_get_reservas_por_usuario_returns_200_con_lista(client):
    id_usuario = str(uuid.uuid4())

    client.post('/api/reserva', json=_payload_reserva(id_usuario))
    client.post('/api/reserva', json=_payload_reserva(id_usuario))

    response = client.get(f'/api/reserva/usuario/{id_usuario}')

    assert response.status_code == 200
    assert response.is_json
    body = response.json
    assert len(body) == 2
    assert all(r['id_usuario'] == id_usuario for r in body)


def test_get_reservas_por_usuario_orden_descendente(client):
    id_usuario = str(uuid.uuid4())

    r1 = client.post('/api/reserva', json=_payload_reserva(id_usuario))
    r2 = client.post('/api/reserva', json=_payload_reserva(id_usuario))
    id_reserva_reciente = r2.json['id_reserva']

    response = client.get(f'/api/reserva/usuario/{id_usuario}')

    assert response.status_code == 200
    body = response.json
    assert len(body) == 2
    # La reserva más reciente debe aparecer primero
    assert body[0]['id_reserva'] == id_reserva_reciente


def test_get_reservas_por_usuario_sin_reservas_returns_200_lista_vacia(client):
    id_usuario = str(uuid.uuid4())

    response = client.get(f'/api/reserva/usuario/{id_usuario}')

    assert response.status_code == 200
    assert response.is_json
    assert response.json == []


def test_get_reservas_por_usuario_invalid_uuid_returns_400(client):
    response = client.get('/api/reserva/usuario/uuid-invalido')

    assert response.status_code == 400
    assert response.is_json
    assert 'badly formed hexadecimal UUID' in response.json['error']


# --- Tests: GET /api/reserva/<id_reserva>/timeline ---

def test_get_timeline_reserva_returns_200(client, monkeypatch):
    id_reserva = str(uuid.uuid4())
    saga_id = uuid.uuid4()

    log_recibido = SimpleNamespace(
        id=uuid.uuid4(),
        tipo_mensaje=SimpleNamespace(value='EVENTO_RECIBIDO'),
        accion='ReservaCreadaIntegracionEvt',
        payload_snapshot={'id_reserva': id_reserva},
        fecha_registro=datetime.datetime(2026, 4, 1, 10, 0, 0)
    )
    log_comando = SimpleNamespace(
        id=uuid.uuid4(),
        tipo_mensaje=SimpleNamespace(value='COMANDO_EMITIDO'),
        accion='ProcesarPagoCmd',
        payload_snapshot={'id_reserva': id_reserva, 'monto': 120000},
        fecha_registro=datetime.datetime(2026, 4, 1, 10, 1, 0)
    )

    saga_fake = SimpleNamespace(
        id=saga_id,
        id_reserva=uuid.UUID(id_reserva),
        id_flujo='RESERVA_ESTANDAR',
        version_ejecucion=1,
        estado_global=SimpleNamespace(value='EN_PROCESO'),
        paso_actual=1,
        historial=[log_comando, log_recibido],
    )

    class DummyRepoSagas:
        def buscar_por_reserva(self, reserva_id):
            assert reserva_id == id_reserva
            return saga_fake

    monkeypatch.setattr(reserva_api_mod, 'RepositorioSagas', DummyRepoSagas)

    response = client.get(f'/api/reserva/{id_reserva}/timeline')

    assert response.status_code == 200
    assert response.is_json
    body = response.json
    assert body['id_reserva'] == id_reserva
    assert body['id_instancia_saga'] == str(saga_id)
    assert body['estado_global'] == 'EN_PROCESO'
    assert body['total_eventos'] == 2
    assert body['timeline'][0]['accion'] == 'ReservaCreadaIntegracionEvt'
    assert body['timeline'][1]['accion'] == 'ProcesarPagoCmd'


def test_get_timeline_reserva_not_found_returns_404(client, monkeypatch):
    id_reserva = str(uuid.uuid4())

    class DummyRepoSagas:
        def buscar_por_reserva(self, _reserva_id):
            return None

    monkeypatch.setattr(reserva_api_mod, 'RepositorioSagas', DummyRepoSagas)

    response = client.get(f'/api/reserva/{id_reserva}/timeline')

    assert response.status_code == 404
    assert response.is_json
    assert 'No se encontró timeline para la reserva' in response.json['error']


def test_get_timeline_reserva_invalid_uuid_returns_400(client):
    response = client.get('/api/reserva/uuid-invalido/timeline')

    assert response.status_code == 400
    assert response.is_json
    assert 'badly formed hexadecimal UUID' in response.json['error']
