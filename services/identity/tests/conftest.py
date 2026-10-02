import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.models.refresh_token import RefreshToken
from app.models.session import Session as SessionModel
from app.models.user import User


@pytest.fixture
def db_session():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()

        db.query(RefreshToken).delete()
        db.query(SessionModel).delete()
        db.query(User).delete()

        db.commit()
        db.close()