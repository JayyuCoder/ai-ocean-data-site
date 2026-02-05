# PowerShell helper to create the conda environment for AI-DATA-SITE
# Run as: Open PowerShell (not necessarily admin) and run this file from project root:
#   .\create_conda_env.ps1

param()

Write-Host "AI-DATA-SITE: Creating conda environment 'ai-ocean' from environment.yml" -ForegroundColor Cyan

# Check for conda
try {
    & conda --version > $null 2>&1
} catch {
    Write-Error "Conda not found. Please install Miniconda or Anaconda and ensure 'conda' is on PATH. https://docs.conda.io/en/latest/miniconda.html"
    exit 1
}

# Create or update environment
$envName = 'ai-ocean'

# If env exists, ask to update
$exists = (& conda env list --json) | Out-String
if ($exists -match '"$envName"') {
    Write-Host "Environment '$envName' already exists. Updating from environment.yml..." -ForegroundColor Yellow
    conda env update -n $envName -f environment.yml --prune
} else {
    Write-Host "Creating environment '$envName'..." -ForegroundColor Green
    conda env create -f environment.yml
}

Write-Host "To activate the environment in PowerShell run:" -ForegroundColor Cyan
Write-Host "    conda activate $envName" -ForegroundColor White
Write-Host "Then run the smoke test:" -ForegroundColor Cyan
Write-Host "    python smoke_test.py" -ForegroundColor White
Write-Host "If you plan to run Streamlit, run:" -ForegroundColor Cyan
Write-Host "    streamlit run frontend/app.py" -ForegroundColor White

Write-Host "Note: If you encounter issues installing TensorFlow on Windows, consider using the CPU wheel or use Miniforge/conda-forge packages. For geospatial libs, conda-forge provides prebuilt packages." -ForegroundColor Yellow
