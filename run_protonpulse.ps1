# ProtonPulse - Standalone Desktop Launcher
# This script launches ProtonPulse as a standalone app
# Right-click this file and select "Run with PowerShell"

Write-Host ""
Write-Host "========================================"
Write-Host "  ProtonPulse v2.3" -ForegroundColor Cyan
Write-Host "  PTM Charge Distribution Analyzer"
Write-Host "========================================"
Write-Host ""

# Get script directory and navigate there
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptPath) {
    Set-Location $scriptPath
}

# Check for virtual environment
$venvPython = ".\.venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Starting ProtonPulse..." -ForegroundColor Green
    Write-Host "Opening browser at http://localhost:8501" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Kill any existing Streamlit processes on port 8501
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Where-Object {$_.CommandLine -match "streamlit"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    # Run streamlit with proper flags to prevent reload loops
    & $venvPython -m streamlit run ptm_charge_input_v2.py `
        --server.port 8501 `
        --server.headless false `
        --browser.gatherUsageStats false `
        --logger.level=error `
        --client.toolbarMode "minimal"
    
    # If we get here, streamlit stopped
    Write-Host ""
    Write-Host "ProtonPulse stopped." -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run setup_env.ps1 first to install dependencies." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Steps:"
    Write-Host "  1. Right-click setup_env.ps1 -> Run with PowerShell"
    Write-Host "  2. Wait for installation to complete"
    Write-Host "  3. Run this script again"
}

Write-Host ""
Read-Host "Press Enter to close"
