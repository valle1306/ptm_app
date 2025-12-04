@echo off
title ProtonPulse - PTM Charge Distribution Analyzer
echo.
echo ========================================
echo   ProtonPulse v2.3
echo   PTM Charge Distribution Analyzer
echo ========================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Starting ProtonPulse...
    echo Opening browser at http://localhost:8501
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    REM Kill any existing Streamlit processes
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq ProtonPulse*" >nul 2>&1
    timeout /t 1 /nobreak >nul
    .venv\Scripts\python.exe -m streamlit run ptm_charge_input_v2.py --server.port 8501 --server.headless false --browser.gatherUsageStats false --logger.level=error --client.toolbarMode "minimal"
    echo.
    echo ProtonPulse stopped.
) else (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup_env.ps1 first to install dependencies.
    echo.
    echo Steps:
    echo   1. Right-click setup_env.ps1 -^> Run with PowerShell
    echo   2. Wait for installation to complete
    echo   3. Run this script again
)

echo.
pause
