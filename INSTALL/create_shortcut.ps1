# Create ProtonPulse Desktop Shortcut
# This script creates a one-click shortcut on your desktop to launch ProtonPulse

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "ProtonPulse.lnk"
$scriptPath = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\run_protonpulse.bat"

Write-Host ""
Write-Host "Creating ProtonPulse Desktop Shortcut..." -ForegroundColor Cyan
Write-Host ""

# Create WScript.Shell COM object
$WshShell = New-Object -ComObject WScript.Shell

# Create the shortcut
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $scriptPath
$shortcut.WorkingDirectory = Split-Path -Parent $scriptPath
$shortcut.Description = "ProtonPulse - PTM Charge Distribution Analyzer"
$shortcut.IconLocation = "C:\Windows\System32\imageres.dll,170"  # Blue chemistry/test tube icon

# Save the shortcut
$shortcut.Save()

Write-Host "✅ Desktop shortcut created: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "  1. Go to your Desktop"
Write-Host "  2. Double-click 'ProtonPulse' shortcut"
Write-Host "  3. App launches automatically!"
Write-Host ""
Write-Host "Press Enter to close this window..."
Read-Host
