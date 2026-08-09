from app.core.database import Base, engine

from app.models.user import User
from app.models.refresh_token import RefreshToken


Base.metadata.create_all(
    bind=engine
)

print("Database tables created successfully!")