# DriveAhead Flask Application Launcher
# Run this script from the website directory

Write-Host "Starting DriveAhead F1 Analytics Platform..." -ForegroundColor Cyan
Write-Host ""

# Navigate to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if app.py exists
if (!(Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found in current directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Display current directory
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Green

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host "Application will be available at: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Start Flask application
python app.py
