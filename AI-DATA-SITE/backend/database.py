from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://ocean_user:ocean_secure_password@localhost:5432/ocean_db"
)

engine = None
SessionLocal = None

def _init_engine():
    """Initialize PostgreSQL engine (fail fast if unavailable)."""
    global engine, SessionLocal

    if engine is not None:
        return

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        future=True
    )

    # Fail immediately if DB is unreachable
    with engine.connect():
        pass

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

def init_db():
    """Create database tables."""
    _init_engine()
    from backend.models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI DB dependency."""
    _init_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
