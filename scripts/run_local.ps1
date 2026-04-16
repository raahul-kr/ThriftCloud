param(
  [switch]$InstallDeps
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"
$frontendPath = Join-Path $repoRoot "frontend"

if ($InstallDeps) {
  Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
  Push-Location $backendPath
  python -m pip install -r requirements.txt
  Pop-Location

  Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
  Push-Location $frontendPath
  npm install
  Pop-Location
}

Write-Host "Starting backend in a new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$backendPath'; uvicorn app.main:app --reload --port 8000`""

Write-Host "Starting frontend in a new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$frontendPath'; npm run dev`""

Write-Host "`nThriftCloud should open at http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend API is available at http://localhost:8000" -ForegroundColor Yellow
