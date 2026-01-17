@echo off
REM CAMVIEW.AI - Quick Start Script
REM Activates venv and launches Streamlit dashboard

echo ================================================
echo CAMVIEW.AI v2.0 - Enhanced Dashboard
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call .venv\Scripts\activate

echo [2/3] Starting Streamlit dashboard...
echo.
echo ================================================
echo Dashboard Features:
echo   - Real-time video processing
echo   - 11 advanced visualizations
echo   - Risk gauge and heatmaps
echo   - Excel/CSV/JSON export
echo ================================================
echo.

streamlit run app.py

pause
