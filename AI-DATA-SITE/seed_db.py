from datetime import date, timedelta

import backend.database as db
from backend.models import OceanMetrics

def seed_db(days=7):
    db.init_db()
    if db.SessionLocal is None:
        raise RuntimeError("Database session not initialized")

    session = db.SessionLocal()
    base_date = date.today()
    rows = []
    for i in range(days):
        d = base_date - timedelta(days=(days - 1 - i))
        rows.append(
            OceanMetrics(
                date=d,
                latitude=6.5,
                longitude=92.5,
                sst=28.0 + i * 0.1,
                dhw=0.5 + i * 0.05,
                ph=8.12 - i * 0.01,
                health_score=80.0 - i * 1.2,
                anomaly=(i == days - 2),
                forecast_ph=None,
            )
        )

    for row in rows:
        session.add(row)
    session.commit()
    session.close()
    print(f"Seeded {days} rows into ocean_metrics.")

if __name__ == "__main__":
    seed_db()
