#!/usr/bin/env python3
"""
Data Retention & Archival Helper

Implements data retention policy: Keep recent data, archive or delete old data.
Can be run manually or via cron job for automated maintenance.

Usage:
  # Delete records older than 90 days (default)
  python3 scripts/data_retention.py --delete-days 90

  # Archive records older than 90 days (optional Postgres COPY to CSV)
  python3 scripts/data_retention.py --archive-days 90 --archive-dir ./archives

  # Show retention policy status
  python3 scripts/data_retention.py --status
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import backend.database as db
from sqlalchemy import text
import pandas as pd


def get_db_age_stats():
    """Get database statistics on data age."""
    with db.engine.connect() as conn:
        # Oldest and newest dates
        r = conn.execute(text("""
            SELECT MIN(date) as oldest, MAX(date) as newest, COUNT(*) as total
            FROM ocean_metrics
        """))
        oldest, newest, total = r.one()
        return {"oldest": oldest, "newest": newest, "total": total}


def delete_old_records(days_back):
    """Delete records older than `days_back` days."""
    cutoff_date = datetime.now().date() - timedelta(days=days_back)
    print(f"Deleting records older than {cutoff_date}...")

    with db.engine.connect() as conn:
        result = conn.execute(text("""
            DELETE FROM ocean_metrics WHERE date < :cutoff
        """), {"cutoff": cutoff_date})
        conn.commit()
        deleted = result.rowcount
        print(f"✓ Deleted {deleted} records")
        return deleted


def archive_old_records(days_back, archive_dir):
    """Archive records older than `days_back` days to CSV."""
    cutoff_date = datetime.now().date() - timedelta(days=days_back)
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)

    print(f"Archiving records older than {cutoff_date} to {archive_path}...")

    df = pd.read_sql(
        "SELECT * FROM ocean_metrics WHERE date < :cutoff ORDER BY date",
        db.engine,
        params={"cutoff": cutoff_date}
    )

    if df.empty:
        print("✓ No records to archive")
        return 0

    archive_file = archive_path / f"ocean_metrics_{cutoff_date}.csv.gz"
    df.to_csv(archive_file, index=False, compression="gzip")
    print(f"✓ Archived {len(df)} records to {archive_file}")

    # Delete after successful archive
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            DELETE FROM ocean_metrics WHERE date < :cutoff
        """), {"cutoff": cutoff_date})
        conn.commit()
        deleted = result.rowcount
        print(f"✓ Deleted {deleted} archived records from DB")

    return len(df)


def show_status():
    """Display data retention status."""
    stats = get_db_age_stats()

    print("\n" + "=" * 60)
    print("DATA RETENTION STATUS")
    print("=" * 60)
    print(f"Total records: {stats['total']:,}")
    print(f"Oldest record: {stats['oldest']}")
    print(f"Newest record: {stats['newest']}")

    if stats['oldest'] and stats['newest']:
        span_days = (stats['newest'] - stats['oldest']).days
        print(f"Data span: {span_days} days")
        if span_days > 0:
            avg_per_day = stats['total'] / span_days
            print(f"Avg records/day: {avg_per_day:.1f}")

    print("\nRETENTION POLICY:")
    print("  - Keep recent: Last 90 days (active)")
    print("  - Archive: 90+ days old (optional)")
    print("  - Delete: After archive (optional)")
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Manage data retention and archival"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show data retention status and exit"
    )
    parser.add_argument(
        "--delete-days",
        type=int,
        default=None,
        help="Delete records older than N days (default: 90)"
    )
    parser.add_argument(
        "--archive-days",
        type=int,
        default=None,
        help="Archive records older than N days (default: 90)"
    )
    parser.add_argument(
        "--archive-dir",
        type=str,
        default="./archives",
        help="Directory to store archives (default: ./archives)"
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Archive without deleting (keep in DB)"
    )

    args = parser.parse_args()

    # Initialize database
    db.init_db()

    if args.status:
        show_status()
        return

    # If no action specified, show status
    if args.delete_days is None and args.archive_days is None:
        show_status()
        print("No retention action specified. Use --delete-days or --archive-days.")
        return

    # Archive and/or delete
    if args.archive_days is not None:
        if args.no_delete:
            print(f"Archiving records older than {args.archive_days} days (no delete)...")
            with db.engine.connect() as conn:
                archivefile = Path(args.archive_dir) / f"ocean_metrics_archive_{datetime.now().isoformat()}.csv.gz"
                df = pd.read_sql(
                    "SELECT * FROM ocean_metrics WHERE date < :cutoff ORDER BY date",
                    db.engine,
                    params={"cutoff": datetime.now().date() - timedelta(days=args.archive_days)}
                )
                if not df.empty:
                    Path(args.archive_dir).mkdir(parents=True, exist_ok=True)
                    df.to_csv(archivefile, index=False, compression="gzip")
                    print(f"✓ Archived {len(df)} records to {archivefile}")
        else:
            archive_old_records(args.archive_days, args.archive_dir)

    elif args.delete_days is not None:
        delete_old_records(args.delete_days)

    # Show updated status
    show_status()


if __name__ == "__main__":
    main()
