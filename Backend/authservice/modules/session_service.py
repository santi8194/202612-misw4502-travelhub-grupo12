"""
Propósito del archivo: Gestión de sesiones persistidas para soportar expiración por inactividad.
Rol dentro del microservicio: Crea, valida y rota refresh tokens asociados a una sesión de usuario.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from config.config import settings
from config.security import create_refresh_token, hash_token
from infrastructure.database import SessionLocal
from infrastructure.models import UserSession


@dataclass
class SessionTokenBundle:
    id: UUID
    refresh_token: str


@dataclass
class SessionRefreshBundle:
    id: UUID
    refresh_token: str
    user_id: UUID
    email: str
    rol: str
    partner_id: UUID | None


class SessionService:
    """
    Servicio responsable de mantener sesiones activas con tiempo de inactividad controlado.
    """

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.utcnow()

    @staticmethod
    def _session_expired(session: UserSession, now: datetime) -> bool:
        idle_limit = session.last_activity_at + timedelta(minutes=settings.SESSION_IDLE_TIMEOUT_MINUTES)
        return session.revoked_at is not None or session.expires_at <= now or idle_limit <= now

    @staticmethod
    def create_session(user_id: UUID) -> SessionTokenBundle:
        db = SessionLocal()
        try:
            now = SessionService._utcnow()
            raw_refresh_token = create_refresh_token()
            session = UserSession(
                user_id=user_id,
                refresh_token_hash=hash_token(raw_refresh_token),
                last_activity_at=now,
                expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return SessionTokenBundle(id=session.id, refresh_token=raw_refresh_token)
        finally:
            db.close()

    @staticmethod
    def validate_session(session_id: str, user_id: UUID, touch_activity: bool = False) -> bool:
        db = SessionLocal()
        try:
            session = db.query(UserSession).filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
            ).first()
            if session is None:
                return False

            now = SessionService._utcnow()
            if SessionService._session_expired(session, now):
                if session.revoked_at is None:
                    session.revoked_at = now
                    session.updated_at = now
                    db.commit()
                return False

            if touch_activity:
                session.last_activity_at = now
                session.updated_at = now
                db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def rotate_refresh_token(refresh_token: str):
        db = SessionLocal()
        try:
            token_hash = hash_token(refresh_token)
            session = db.query(UserSession).filter(UserSession.refresh_token_hash == token_hash).first()
            if session is None:
                return None

            now = SessionService._utcnow()
            if SessionService._session_expired(session, now):
                if session.revoked_at is None:
                    session.revoked_at = now
                    session.updated_at = now
                    db.commit()
                return None

            new_refresh_token = create_refresh_token()
            session.refresh_token_hash = hash_token(new_refresh_token)
            session.last_activity_at = now
            session.updated_at = now
            rol = session.user.roles[0].name if session.user.roles else "USER"
            partner_id = session.user.partner_id
            email = session.user.email
            user_id = session.user.id
            db.commit()
            db.refresh(session)
            return SessionRefreshBundle(
                id=session.id,
                refresh_token=new_refresh_token,
                user_id=user_id,
                email=email,
                rol=rol,
                partner_id=partner_id,
            )
        finally:
            db.close()