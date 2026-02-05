#!/usr/bin/env powershell
# Quick Start Guide for AI Ocean Data Site

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Ocean Data Site - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$ProjectDir = "C:\ai-ocean-data-site\AI-DATA-SITE"
Set-Location $ProjectDir

Write-Host "[1/5] Checking project files..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\main.py",
    "backend\database.py",
    "frontend\app.py",
    "ml\model.py",
    "pipeline\run_pipeline.py",
    "requirements.txt",
    "smoke_test.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file MISSING!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[2/5] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  ✅ Virtual environment activated" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Running smoke test..." -ForegroundColor Yellow
& python smoke_test.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ All files verified" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Smoke test found issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Starting FastAPI backend..." -ForegroundColor Yellow
Write-Host "  Starting on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the backend in a new window
$backendCommand = "cd `"$ProjectDir`"; & .\venv\Scripts\Activate.ps1; uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process PowerShell -ArgumentList "-Command `"$backendCommand`""

Start-Sleep -Seconds 3

Write-Host "[5/5] Opening dashboard..." -ForegroundColor Yellow
Write-Host "  Starting Streamlit on http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
& .\venv\Scripts\streamlit.exe run frontend\app.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "  📊 Dashboard: http://localhost:8501" -ForegroundColor White
Write-Host "  🔧 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  📈 API Root: http://127.0.0.1:8000" -ForegroundColor White
Write-Host ""
