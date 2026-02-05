#!/usr/bin/env python
"""
Setup script to create and configure Python virtual environment
"""
import subprocess
import sys
import os

# Create venv
env_path = os.path.join(os.getcwd(), "venv")
print(f"Creating virtual environment at {env_path}...")
subprocess.run([sys.executable, "-m", "venv", env_path], check=True)

# Activate venv and install packages
venv_python = os.path.join(env_path, "Scripts", "python.exe")
venv_pip = os.path.join(env_path, "Scripts", "pip.exe")

packages = [
    "pandas",
    "numpy",
    "fastapi",
    "uvicorn[standard]",
    "streamlit",
    "pydeck",
    "plotly",
    "python-dotenv",
    "python-dateutil",
    "openpyxl",
    "scikit-learn",
    "requests",
    "sqlalchemy",
    "psycopg2-binary",
    "xarray",
    "netCDF4",
    "geopandas",
    "shapely",
    "pyproj",
]

print(f"Installing packages using {venv_pip}...")
for package in packages:
    print(f"  Installing {package}...")
    subprocess.run([venv_pip, "install", "--quiet", package])

print(f"\nVirtual environment created successfully at {env_path}")
print(f"To activate, run: {env_path}\\Scripts\\activate.bat")
print(f"Or in PowerShell: & '{env_path}\\Scripts\\Activate.ps1'")
