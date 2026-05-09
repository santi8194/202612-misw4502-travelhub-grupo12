"""
Pruebas unitarias para UnidadTrabajoHibrida: commit, rollback, context manager, eventos.
"""
from unittest.mock import MagicMock, patch
import uuid

from config.uow import UnidadTrabajoHibrida
from modulos.reserva.dominio.eventos import ReservaPendiente
from seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass


@dataclass
class ComandoTest(Comando):
    """Comando de prueba para testing."""
    id_test: uuid.UUID


# --- Pruebas de context manager ---

def test_uow_context_manager_entra_y_sale_correctamente():
    """Verifica que UnidadTrabajoHibrida funciona como context manager."""
    despachador_mock = MagicMock()
    
    with UnidadTrabajoHibrida(despachador=despachador_mock) as uow:
        assert uow is not None
    
    despachador_mock.cerrar.assert_called_once()


@patch("config.uow.db")
def test_uow_context_manager_hace_rollback_en_excepcion(mock_db):
    """Verifica que el context manager hace rollback si hay una excepción."""
    despachador_mock = MagicMock()
    
    try:
        with UnidadTrabajoHibrida(despachador=despachador_mock) as uow:
            raise ValueError("Error de prueba")
    except ValueError:
        pass
    
    mock_db.session.rollback.assert_called_once()
    despachador_mock.cerrar.assert_called_once()


# --- Pruebas de agregar_eventos ---

def test_agregar_eventos_almacena_eventos_en_lista():
    """Verifica que agregar_eventos almacena eventos en la lista interna."""
    uow = UnidadTrabajoHibrida(despachador=MagicMock())
    
    evento1 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    evento2 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    
    uow.agregar_eventos([evento1, evento2])
    
    assert len(uow._eventos) == 2


def test_agregar_eventos_acumula_eventos():
    """Verifica que agregar_eventos acumula eventos en múltiples llamadas."""
    uow = UnidadTrabajoHibrida(despachador=MagicMock())
    
    evento1 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    evento2 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    
    uow.agregar_eventos([evento1])
    uow.agregar_eventos([evento2])
    
    assert len(uow._eventos) == 2


# --- Pruebas de commit ---

@patch("config.uow.db")
def test_commit_hace_commit_en_bd(mock_db):
    """Verifica que commit hace commit en la base de datos."""
    despachador_mock = MagicMock()
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    uow.commit()
    
    mock_db.session.commit.assert_called_once()


@patch("config.uow.db")
def test_commit_publica_eventos_de_dominio_despues_de_bd(mock_db):
    """Verifica que commit publica eventos de dominio después del commit de BD."""
    despachador_mock = MagicMock()
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    evento = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    uow.agregar_eventos([evento])
    
    uow.commit()
    
    mock_db.session.commit.assert_called_once()
    despachador_mock.publicar_evento.assert_called_once()
    assert despachador_mock.publicar_evento.call_args[0][0] == evento


@patch("config.uow.db")
def test_commit_publica_comandos_con_exchange_correcto(mock_db):
    """Verifica que commit publica comandos con el exchange de comandos."""
    despachador_mock = MagicMock()
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    comando = ComandoTest(id_test=uuid.uuid4())
    uow.agregar_eventos([comando])
    
    uow.commit()
    
    mock_db.session.commit.assert_called_once()
    despachador_mock.publicar_evento.assert_called_once()
    call_args = despachador_mock.publicar_evento.call_args
    assert call_args[0][0] == comando
    assert call_args[0][1] == 'travelhub.commands.exchange'


@patch("config.uow.db")
def test_commit_limpia_eventos_despues_de_publicar(mock_db):
    """Verifica que commit limpia la lista de eventos después de publicarlos."""
    despachador_mock = MagicMock()
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    evento = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    uow.agregar_eventos([evento])
    
    uow.commit()
    
    assert len(uow._eventos) == 0


@patch("config.uow.db")
def test_commit_no_publica_eventos_si_commit_bd_falla(mock_db):
    """Verifica que commit no publica eventos si el commit de BD falla."""
    mock_db.session.commit.side_effect = Exception("Error de BD")
    despachador_mock = MagicMock()
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    evento = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    uow.agregar_eventos([evento])
    
    try:
        uow.commit()
    except Exception:
        pass
    
    despachador_mock.publicar_evento.assert_not_called()
    mock_db.session.rollback.assert_called_once()


@patch("config.uow.db")
def test_commit_continua_si_falla_publicacion_de_un_evento(mock_db):
    """Verifica que commit continúa publicando eventos aunque uno falle."""
    despachador_mock = MagicMock()
    despachador_mock.publicar_evento.side_effect = [Exception("Error de publicación"), None]
    
    uow = UnidadTrabajoHibrida(despachador=despachador_mock)
    
    evento1 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    evento2 = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    uow.agregar_eventos([evento1, evento2])
    
    uow.commit()
    
    assert despachador_mock.publicar_evento.call_count == 2


# --- Pruebas de rollback ---

@patch("config.uow.db")
def test_rollback_hace_rollback_en_bd(mock_db):
    """Verifica que rollback hace rollback en la base de datos."""
    uow = UnidadTrabajoHibrida(despachador=MagicMock())
    
    uow.rollback()
    
    mock_db.session.rollback.assert_called_once()


@patch("config.uow.db")
def test_rollback_limpia_eventos(mock_db):
    """Verifica que rollback limpia la lista de eventos."""
    uow = UnidadTrabajoHibrida(despachador=MagicMock())
    
    evento = ReservaPendiente(
        id_reserva=uuid.uuid4(),
        id_usuario=uuid.uuid4(),
        id_categoria=uuid.uuid4(),
    )
    uow.agregar_eventos([evento])
    
    uow.rollback()
    
    assert len(uow._eventos) == 0


# --- Pruebas de despachador por defecto ---

@patch("config.uow.DespachadorRabbitMQ")
def test_uow_usa_despachador_rabbitmq_por_defecto(mock_despachador_class):
    """Verifica que UnidadTrabajoHibrida usa DespachadorRabbitMQ por defecto."""
    mock_despachador_instance = MagicMock()
    mock_despachador_class.return_value = mock_despachador_instance
    
    uow = UnidadTrabajoHibrida()
    
    mock_despachador_class.assert_called_once()
    assert uow._despachador == mock_despachador_instance


def test_uow_acepta_despachador_inyectado():
    """Verifica que UnidadTrabajoHibrida acepta un despachador inyectado."""
    despachador_custom = MagicMock()
    
    uow = UnidadTrabajoHibrida(despachador=despachador_custom)
    
    assert uow._despachador == despachador_custom
