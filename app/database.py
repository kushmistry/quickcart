from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

# Create engine using the computed DATABASE_URL from settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=False
)

# Session factory for DB transactions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# FastAPI dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()