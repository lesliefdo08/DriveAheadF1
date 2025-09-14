# DriveAhead F1 Analytics Platform - Windows Production Runner

Write-Host "🏎️  Starting DriveAhead F1 Analytics Platform in production mode..." -ForegroundColor Green

# Load environment variables from .env file
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

# Create necessary directories if they don't exist
New-Item -ItemType Directory -Force -Path cache | Out-Null
New-Item -ItemType Directory -Force -Path models | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Set production environment
$env:FLASK_ENV = "production"
$env:FLASK_DEBUG = "False"

# Start the application
Write-Host "Starting DriveAhead F1 Analytics Platform..." -ForegroundColor Yellow

try {
    # Try to use Gunicorn if available
    if (Get-Command gunicorn -ErrorAction SilentlyContinue) {
        Write-Host "Starting with Gunicorn..." -ForegroundColor Cyan
        gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 30 --log-level info app:app
    } else {
        Write-Host "Gunicorn not found. Starting with Flask development server..." -ForegroundColor Yellow
        Write-Host "For production, install Gunicorn: pip install gunicorn" -ForegroundColor Red
        python app.py
    }
} catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ DriveAhead F1 Analytics Platform started successfully!" -ForegroundColor Green
Write-Host "📊 Application available at: http://localhost:5000" -ForegroundColor Cyan