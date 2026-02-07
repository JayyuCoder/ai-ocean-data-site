"""
Simple migration helper: copy rows from the local SQLite demo DB to a Postgres DB
pointed to by the `DATABASE_URL` environment variable.

Usage:
  DATABASE_URL=postgresql://user:pass@localhost:5432/dbname \
    python3 scripts/migrate_sqlite_to_postgres.py

This script uses SQLAlchemy. If a driver is missing (e.g. psycopg2), it will
report the error and exit.
"""
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.exc import SQLAlchemyError

SQLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'ocean_demo.db')
SQLITE_URL = f"sqlite:///{SQLITE_PATH}"
PG_URL = os.environ.get('DATABASE_URL')

if not PG_URL:
    print("DATABASE_URL not set. Set it to your Postgres connection string and retry.")
    sys.exit(2)

print(f"Reading from SQLite: {SQLITE_URL}")
print(f"Writing to Postgres: {PG_URL}")

try:
    sqlite_engine = create_engine(SQLITE_URL)
    pg_engine = create_engine(PG_URL)
except Exception as e:
    print("Error creating engines:", e)
    print("Ensure SQLAlchemy and a Postgres DB driver (psycopg2 or asyncpg) are installed.")
    sys.exit(3)

sqlite_meta = MetaData()
pg_meta = MetaData()

try:
    sqlite_meta.reflect(bind=sqlite_engine)
except SQLAlchemyError as e:
    print("Failed to reflect sqlite DB:", e)
    sys.exit(4)

# Attempt to find a sensible table to copy. The demo uses 'ocean_metrics' or similar.
candidate_tables = [t for t in sqlite_meta.tables.keys()]
if not candidate_tables:
    print("No tables found in sqlite DB; nothing to migrate.")
    sys.exit(0)

print("Found tables in sqlite:", candidate_tables)

for table_name in candidate_tables:
    print(f"Migrating table: {table_name}")
    sqlite_table = Table(table_name, sqlite_meta, autoload_with=sqlite_engine)
    # Create table in Postgres if not exists by reflecting into pg_meta and using metadata.create_all
    # Copy table schema into pg_meta using to_metadata to avoid reusing Column objects
    try:
        sqlite_table.to_metadata(pg_meta)
    except Exception:
        # Fallback: try creating an empty table with same name (best-effort)
        pg_table = Table(table_name, pg_meta)
    try:
        pg_meta.create_all(bind=pg_engine)
        # Try to obtain the created table object from pg_meta
        pg_table = pg_meta.tables.get(table_name)
    except Exception as e:
        print(f"Warning: could not create table {table_name} in Postgres: {e}")

    # Copy rows in chunks
    chunk = 500
    offset = 0
    total = 0
    with sqlite_engine.connect() as src_conn, pg_engine.connect() as dst_conn:
        while True:
            sel = select(sqlite_table).limit(chunk).offset(offset)
            rows = src_conn.execute(sel).fetchall()
            if not rows:
                break
            # SQLAlchemy Row objects expose a mapping interface; use _mapping to get plain dict
            data = [dict(r._mapping) for r in rows]
            try:
                dst_conn.execute(pg_table.insert(), data)
                dst_conn.commit()
            except Exception as e:
                print(f"Error inserting chunk at offset {offset}: {e}")
                print("You can re-run this script after fixing the issue; partial data may exist.")
                sys.exit(5)
            total += len(data)
            offset += chunk
        print(f"Migrated {total} rows for table {table_name}")

print("Migration complete.")
