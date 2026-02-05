"""
Lightweight smoke test for AI-DATA-SITE.
This script checks that Python is available, and that critical project files exist.
Run locally after installing Python and required packages.

Usage:
  python smoke_test.py

It does NOT require project dependencies; it's a minimal repo sanity check.
"""
import os
import sys

print("AI-DATA-SITE smoke test")
print("Python executable:", sys.executable)
print("Python version:", sys.version.splitlines()[0])

root = os.path.dirname(os.path.abspath(__file__))
print("Project root:", root)

files_to_check = [
    "pipeline/fetch_noaa.py",
    "pipeline/fetch_allen.py",
    "pipeline/clean_transform.py",
    "pipeline/merge_data.py",
    "pipeline/run_pipeline.py",
    "ml/model.py",
    "backend/main.py",
    "backend/database.py",
    "backend/models.py",
    "frontend/app.py",
    "scheduler/scheduler.py",
    "docker-compose.yml",
    "Dockerfile",
    "requirements.txt",
]

missing = []
for f in files_to_check:
    path = os.path.join(root, f)
    exists = os.path.exists(path)
    print(f" - {f}: {'OK' if exists else 'MISSING'}")
    if not exists:
        missing.append(f)

if missing:
    print()
    print("Missing files detected. Please ensure you run this script from the project root and that files were not removed.")
    print("Missing:")
    for m in missing:
        print("  -", m)
    sys.exit(2)

print()
print("Basic repo sanity checks passed.")
print()
print("Next steps to run full (optional):")
print("  1) Install Python 3.10+ from https://www.python.org/downloads/ or Microsoft Store")
print("  2) Create virtual env: python -m venv .venv")
print("  3) Activate: .venv\\Scripts\\Activate.ps1  (PowerShell) or .venv\\Scripts\\activate")
print("  4) Install deps: pip install -r requirements.txt")
print("  5) Run pipeline test: python pipeline/run_pipeline.py")
print("  6) Launch dashboard: streamlit run frontend/app.py")
print()
print("Smoke test complete.")
