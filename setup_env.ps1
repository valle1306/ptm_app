# setup_env.ps1 - Create and populate a .venv for this project
# Run this in PowerShell from the project root: `.uild\setup_env.ps1` or `.\
# Steps:
# 1) Ensure you have a full CPython installed (download from https://www.python.org/downloads/)
#    - During install: check "Add Python to PATH" (recommended)
# 2) Then run this script from the project root in PowerShell.

Write-Output "== Setup environment helper =="

# Show current python
Write-Output "Detecting python on PATH..."
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) {
    Write-Error "No 'python' command found on PATH. Please install CPython from https://python.org and ensure it's on PATH."
    exit 2
}
Write-Output "Using: $($py.Path)"

# Create venv
$venvPath = Join-Path (Get-Location) '.venv'
if (Test-Path $venvPath) {
    Write-Output ".venv already exists. Skipping creation."
} else {
    Write-Output "Creating virtual environment at .venv..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create venv. Ensure you are running a full CPython installation (not the Microsoft Store stub)."
        exit 3
    }
    Write-Output "Created .venv"
}

# Activate venv for this session (use this in your interactive shell; script will continue to call the venv python directly)
$activateScript = Join-Path $venvPath 'Scripts\Activate.ps1'
if (Test-Path $activateScript) {
    Write-Output "To activate the virtual environment in this shell, run:`n    .\ .venv\Scripts\Activate.ps1"
} else {
    Write-Warning "Activation script not found; the venv may not have been created correctly."
}

# Install/upgrade pip and requirements using the venv's python (no activation necessary)
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment python not found at $venvPython. Aborting install."
    exit 4
}

Write-Output "Upgrading pip, setuptools and wheel inside venv..."
& $venvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { Write-Warning "pip upgrade returned non-zero exit code." }

if (Test-Path 'requirements.txt') {
    Write-Output "Installing dependencies from requirements.txt..."
    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Write-Warning "pip install returned non-zero exit code." }
} else {
    Write-Warning "No requirements.txt found in project root. Skipping dependency install."
}

Write-Output "== Done. To run the app:"
Write-Output "1) Activate the venv in PowerShell (optional but recommended): .\\.venv\\Scripts\\Activate.ps1"
Write-Output "2) Run: streamlit run ptm_charge_input.py"
Write-Output "If activation is blocked by execution policy, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
