#!/usr/bin/env python
"""
Enhanced smoke test for AI-DATA-SITE with import validation.
Tests files exist + imports work for installed packages.
"""
import os
import sys

print("=" * 60)
print("AI-DATA-SITE Enhanced Smoke Test")
print("=" * 60)
print(f"Python: {sys.executable}")
print(f"Version: {sys.version.splitlines()[0]}")
print()

# ===== CHECK FILES =====
print("[1/3] Checking critical files...")
root = os.path.dirname(os.path.abspath(__file__))

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
    status = "✅" if exists else "❌"
    print(f"  {status} {f}")
    if not exists:
        missing.append(f)

print()

# ===== CHECK IMPORTS =====
print("[2/3] Checking Python imports...")
imports_to_test = {
    "numpy": "Data processing",
    "pandas": "Data manipulation",
    "fastapi": "Web framework",
    "uvicorn": "ASGI server",
    "streamlit": "Dashboard",
    "plotly": "Visualization",
    "pydeck": "Map rendering",
    "scikit-learn": "ML algorithms",
    "sqlalchemy": "Database ORM",
    "psycopg2": "PostgreSQL adapter",
    "xarray": "Scientific data",
    "netCDF4": "Data format",
    "shapely": "Geometry (optional)",
    "geopandas": "Geospatial (optional)",
    "gdal": "GDAL tools (optional)",
    "tensorflow": "Deep learning (optional)",
}

installed = {}
for pkg, desc in imports_to_test.items():
    try:
        __import__(pkg)
        print(f"  ✅ {pkg:20} - {desc}")
        installed[pkg] = True
    except ImportError:
        print(f"  ⚠️  {pkg:20} - {desc} [MISSING]")
        installed[pkg] = False

print()

# ===== SUMMARY =====
print("[3/3] Summary")
print("-" * 60)

total_files = len(files_to_check)
present_files = total_files - len(missing)
print(f"Files:   {present_files}/{total_files} present")

installed_count = sum(1 for v in installed.values() if v)
total_pkgs = len(imports_to_test)
print(f"Imports: {installed_count}/{total_pkgs} available")

print()

# ===== RECOMMENDATIONS =====
if missing:
    print("⚠️  Missing Files:")
    for m in missing:
        print(f"   - {m}")
    print("   → Run this script from the project root directory")
    print()

optional_missing = [k for k, v in installed.items() if not v and k in ["shapely", "geopandas", "gdal", "tensorflow"]]
required_missing = [k for k, v in installed.items() if not v and k not in ["shapely", "geopandas", "gdal", "tensorflow"]]

if required_missing:
    print("❌ Missing Required Packages:")
    for pkg in required_missing:
        print(f"   - {pkg}")
    print("   → Run: pip install -r requirements.txt")
    print()

if optional_missing:
    print("⚠️  Missing Optional Packages (geospatial/ML):")
    for pkg in optional_missing:
        print(f"   - {pkg}")
    print("   → For geospatial: conda install -c conda-forge gdal geopandas fiona rtree")
    print("   → For TensorFlow: pip install tensorflow")
    print()

if not missing and not required_missing:
    print("✅ All critical files and required packages present!")
    print("   Ready to run:")
    print()
    print("   1. Start FastAPI:")
    print("      uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
    print()
    print("   2. Start Streamlit (in new terminal):")
    print("      streamlit run frontend/app.py")
    print()
    print("   3. Run pipeline manually (optional):")
    print("      python pipeline/run_pipeline.py")
    print()

print("=" * 60)
