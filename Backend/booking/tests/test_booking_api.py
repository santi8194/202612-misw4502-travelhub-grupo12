import uuid

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