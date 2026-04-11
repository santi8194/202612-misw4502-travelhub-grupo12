import uuid
from unittest.mock import MagicMock

import modulos.reserva.infraestructura.api as reserva_api_mod

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
    assert body['mensaje'] == 'Reserva creada en estado HOLD (15 min)'
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