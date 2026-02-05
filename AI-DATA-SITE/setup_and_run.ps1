<#
Setup and run automation for AI-DATA-SITE (Windows PowerShell)
Usage (run from project root):
  .\setup_and_run.ps1

What it does:
- Ensures `conda` exists
- Runs `create_conda_env.ps1` to create/update `ai-ocean` env
- Runs `conda run -n ai-ocean python smoke_test.py`
- Optionally runs `conda run -n ai-ocean python test_db.py`
- Starts backend (uvicorn) and frontend (streamlit) via `conda run` in new processes

Note: Run interactively in PowerShell. If `conda` is not installed the script will instruct you.
#>

$ErrorActionPreference = 'Stop'

Write-Host "AI-DATA-SITE: Setup & Run script" -ForegroundColor Cyan

# Check for conda
try {
    & conda --version > $null 2>&1
} catch {
    Write-Error "Conda not found. Install Miniconda (https://docs.conda.io/en/latest/miniconda.html) and re-run this script."
    exit 1
}

# Create/update environment
Write-Host "Creating/updating conda env from environment.yml..." -ForegroundColor Green
if (Test-Path .\create_conda_env.ps1) {
    & .\create_conda_env.ps1
} else {
    Write-Warning "create_conda_env.ps1 not found. Make sure environment.yml exists and create manually: conda env create -f environment.yml" -ForegroundColor Yellow
}

# Smoke test inside env
Write-Host "Running smoke_test.py inside conda env..." -ForegroundColor Green
& conda run -n ai-ocean python smoke_test.py

# Optional DB test
$doDb = Read-Host "Run database connectivity test now? (y/n)"
if ($doDb -match '^[Yy]') {
    Write-Host "Running test_db.py..." -ForegroundColor Green
    & conda run -n ai-ocean python test_db.py
}

# Start backend (uvicorn)
Write-Host "Starting FastAPI (uvicorn) in background..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath conda -ArgumentList 'run -n ai-ocean uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000' -WindowStyle Normal

# Start Streamlit
Write-Host "Starting Streamlit in background..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath conda -ArgumentList 'run -n ai-ocean streamlit run frontend/app.py' -WindowStyle Normal

Write-Host "All done. Backend: http://127.0.0.1:8000/docs  |  Dashboard: http://localhost:8501" -ForegroundColor Cyan
