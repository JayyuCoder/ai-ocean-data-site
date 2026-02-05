"""
Simple DB connectivity test. Edit `DATABASE_URL` env var or the default below.
"""
import os
from sqlalchemy import create_engine, text

# Default matches docker-compose; change if needed
db_url = os.getenv(
    "DATABASE_URL",
    "postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db"
)
print("Testing DB_URL:", db_url)

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1")).fetchone()
        print("DB response:", r)
except Exception as e:
    print("DB connection failed:", e)
    raise SystemExit(2)
