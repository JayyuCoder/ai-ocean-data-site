from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db"
)

# Always try to use the specified database URL, but don't connect yet
engine = None
SessionLocal = None

def _init_engine():
    """Initialize engine with fallback to SQLite"""
    global engine, SessionLocal
    if engine is not None:
        return
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
        # Test connection immediately
        with engine.connect() as conn:
            pass
    except Exception as e:
        # Fall back to SQLite for demo mode
        print(f"⚠️  PostgreSQL unavailable ({type(e).__name__}), using SQLite for demo")
        engine = create_engine("sqlite:///./ocean_demo.db", echo=False)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    _init_engine()
    try:
        from backend.models import Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️  Database table creation skipped: {type(e).__name__}")

def get_db():
    _init_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


