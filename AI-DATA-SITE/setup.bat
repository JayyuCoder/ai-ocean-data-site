@echo off
cd /d C:\ai-ocean-data-site\AI-DATA-SITE
echo Creating Python virtual environment...
python -m venv venv

echo.
echo Activating venv and installing packages...
call venv\Scripts\activate.bat

echo Installing core packages...
pip install --upgrade pip setuptools wheel
pip install pandas numpy fastapi uvicorn streamlit pydeck plotly python-dotenv python-dateutil openpyxl
pip install scikit-learn requests sqlalchemy psycopg2-binary xarray netCDF4
pip install geopandas shapely pyproj rtree

echo.
echo Setup complete! To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo Then you can run:
echo   python smoke_test.py
echo   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
echo   streamlit run frontend/app.py
