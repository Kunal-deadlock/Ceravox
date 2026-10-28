<#
.SYNOPSIS
    One-command development startup script for Ceravox.
.DESCRIPTION
    Checks local prerequisites (Ollama, Python venv, dashboard dependencies),
    launches the FastAPI backend and Vite dashboard, displays local URLs,
    and provides actionable guidance if any local models are missing.
#>

$ErrorActionPreference = "Stop"

Write-Host "`n=== Ceravox Development Startup ===" -ForegroundColor Cyan
Write-Host "Local-first offline voice AI workstation`n"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$dashboardDir = Join-Path $repoRoot "dashboard"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"

# 1. Check Python virtual environment
if (-not (Test-Path $pythonExe)) {
    Write-Warning "Python virtual environment not found at $pythonExe"
    Write-Host "Set it up with:" -ForegroundColor Yellow
    Write-Host "  cd backend"
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

# 2. Check Dashboard node_modules
$nodeModules = Join-Path $dashboardDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Warning "Dashboard dependencies not installed at $nodeModules"
    Write-Host "Set them up with:" -ForegroundColor Yellow
    Write-Host "  cd dashboard"
    Write-Host "  npm ci"
    exit 1
}

# 3. Check / Start Ollama
Write-Host "[1/3] Checking Ollama service..." -NoNewline
$ollamaRunning = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($res) { $ollamaRunning = $true }
} catch {
    $ollamaRunning = $false
}

if ($ollamaRunning) {
    Write-Host " OK (running on http://127.0.0.1:11434)" -ForegroundColor Green
} else {
    Write-Host " Not running." -ForegroundColor Yellow
    $ollamaCmd = Get-Command "ollama" -ErrorAction SilentlyContinue
    if ($ollamaCmd) {
        Write-Host "Starting Ollama in background..." -ForegroundColor Cyan
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Note: 'ollama' CLI not found on PATH. If using Ollama, install it from https://ollama.com and run 'ollama pull qwen2.5:3b'." -ForegroundColor Yellow
    }
}

# 4. Start Backend
Write-Host "[2/3] Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendDir'; Write-Host '--- Ceravox Backend ---' -ForegroundColor Cyan; .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
)

# 5. Start Dashboard
Write-Host "[3/3] Starting Vite dashboard on http://127.0.0.1:5173..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$dashboardDir'; Write-Host '--- Ceravox Dashboard ---' -ForegroundColor Cyan; npm run dev -- --host 127.0.0.1"
)

# 6. Display Service Status and Links
Write-Host "`nCeravox is running!" -ForegroundColor Green
Write-Host "--------------------------------------------------------"
Write-Host "  Dashboard:      http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  System Status:  http://127.0.0.1:5173/system-status" -ForegroundColor White
Write-Host "  Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Docs:       http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "--------------------------------------------------------"

# 7. Model Guidance & Troubleshooting
Write-Host "`nIf any model or component shows 'unavailable' on the System Status page:" -ForegroundColor Yellow
Write-Host "  - ASR (Whisper) / TTS (Kokoro):"
Write-Host "      cd backend"
Write-Host "      .venv\Scripts\python.exe scripts\install_models.py --download"
Write-Host "  - Ollama (Qwen2.5:3b):"
Write-Host "      ollama pull qwen2.5:3b"
Write-Host "  - Verify offline readiness anytime with:"
Write-Host "      cd backend"
Write-Host "      .venv\Scripts\python.exe scripts\check_offline.py --offline`n"
