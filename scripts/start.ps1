# Ceravox One-Click Startup Script
# Starts backend + Cloudflare tunnel, then auto-updates Vercel so the live site always works.
#
# FIRST-TIME SETUP (run once):
#   1. Copy .env.local.example to .env.local and fill in your VERCEL_TOKEN
#      (Create a token at: https://vercel.com/account/tokens)
#   2. Run: .\scripts\start.ps1
#
# Every time before a demo: just run .\scripts\start.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent

# ── Banner ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       Ceravox  —  One-Click Demo Launcher       ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Load .env.local ──────────────────────────────────────────────────────────
$envFile = Join-Path $Root ".env.local"
if (-not (Test-Path $envFile)) {
    Write-Host "  [ERROR] .env.local not found." -ForegroundColor Red
    Write-Host "  Copy .env.local.example -> .env.local and add your VERCEL_TOKEN." -ForegroundColor Yellow
    Write-Host "  Get a token at: https://vercel.com/account/tokens" -ForegroundColor Yellow
    exit 1
}
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#=\s]+)\s*=\s*(.+)$") {
        Set-Item -Path "Env:\$($Matches[1].Trim())" -Value $Matches[2].Trim()
    }
}

$VERCEL_TOKEN   = $env:VERCEL_TOKEN
$VERCEL_PROJECT = if ($env:VERCEL_PROJECT) { $env:VERCEL_PROJECT } else { "ceravox-nova" }
$DASHBOARD_URL  = "https://$VERCEL_PROJECT.vercel.app"
$BACKEND_PORT   = 8000
$PythonBin      = Join-Path $Root "backend\.venv\Scripts\python.exe"
$CloudflaredBin = Join-Path $Root "scripts\cloudflared.exe"

if (-not $VERCEL_TOKEN -or $VERCEL_TOKEN -eq "your_vercel_token_here") {
    Write-Host "  [ERROR] VERCEL_TOKEN is missing or placeholder. Edit .env.local." -ForegroundColor Red
    Write-Host "  Get a token at: https://vercel.com/account/tokens" -ForegroundColor Yellow
    exit 1
}

# ── Step 1: Start FastAPI backend ─────────────────────────────────────────────
Write-Host "  [1/4] Starting Ceravox backend (port $BACKEND_PORT)..." -ForegroundColor Green

$env:CERAVOX_DASHBOARD_URL = $DASHBOARD_URL
$env:CERAVOX_COOKIE_SECURE = "true"

$backendProcess = Start-Process `
    -FilePath $PythonBin `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$BACKEND_PORT") `
    -WorkingDirectory (Join-Path $Root "backend") `
    -PassThru -WindowStyle Minimized

# Poll until backend responds
$ready = $false
Write-Host "       Waiting for backend..." -NoNewline -ForegroundColor Gray
for ($i = 0; $i -lt 25; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline -ForegroundColor Gray
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BACKEND_PORT/v1/auth/status" `
            -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
}
Write-Host ""
if (-not $ready) {
    Write-Host "  [ERROR] Backend failed to start. Check your Python environment." -ForegroundColor Red
    exit 1
}
Write-Host "       ✓ Backend ready at http://127.0.0.1:$BACKEND_PORT" -ForegroundColor Green

# ── Step 2: Start Cloudflare tunnel ──────────────────────────────────────────
Write-Host "  [2/4] Starting Cloudflare tunnel..." -ForegroundColor Green

if (-not (Test-Path $CloudflaredBin)) {
    Write-Host "       Downloading cloudflared..." -ForegroundColor Yellow
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $CloudflaredBin -UseBasicParsing
}

$tunnelLog = Join-Path $env:TEMP "ceravox-tunnel-$PID.log"
if (Test-Path $tunnelLog) { Remove-Item $tunnelLog -Force }

$tunnelProcess = Start-Process `
    -FilePath $CloudflaredBin `
    -ArgumentList @("tunnel", "--url", "http://127.0.0.1:$BACKEND_PORT") `
    -RedirectStandardError $tunnelLog `
    -PassThru -WindowStyle Hidden

# Wait for tunnel URL in log
$tunnelUrl = $null
Write-Host "       Waiting for tunnel URL..." -NoNewline -ForegroundColor Gray
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline -ForegroundColor Gray
    if (Test-Path $tunnelLog) {
        $content = Get-Content $tunnelLog -Raw -ErrorAction SilentlyContinue
        if ($content -match "https://[a-z0-9\-]+\.trycloudflare\.com") {
            $tunnelUrl = $Matches[0]
            break
        }
    }
}
Write-Host ""
if (-not $tunnelUrl) {
    Write-Host "  [ERROR] Could not get tunnel URL. Check internet connection." -ForegroundColor Red
    $backendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "       ✓ Tunnel: $tunnelUrl" -ForegroundColor Green

# ── Step 3: Update Vercel VITE_API_BASE_URL ───────────────────────────────────
Write-Host "  [3/4] Updating Vercel environment variable..." -ForegroundColor Green
$headers = @{
    Authorization  = "Bearer $VERCEL_TOKEN"
    "Content-Type" = "application/json"
}

try {
    $projectResp = Invoke-RestMethod `
        -Uri "https://api.vercel.com/v9/projects/$VERCEL_PROJECT/env" `
        -Headers $headers -Method Get -ErrorAction Stop
} catch {
    Write-Host "  [ERROR] Vercel API call failed. Is your VERCEL_TOKEN valid?" -ForegroundColor Red
    Write-Host "  $_" -ForegroundColor Red
    $backendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
    $tunnelProcess  | Stop-Process -Force -ErrorAction SilentlyContinue
    exit 1
}

$envVar = $projectResp.envs | Where-Object { $_.key -eq "VITE_API_BASE_URL" } | Select-Object -First 1
$envBody = @{
    value  = $tunnelUrl
    type   = "plain"
    target = @("production", "preview")
} | ConvertTo-Json

if ($envVar) {
    Invoke-RestMethod `
        -Uri "https://api.vercel.com/v9/projects/$VERCEL_PROJECT/env/$($envVar.id)" `
        -Headers $headers -Method Patch -Body $envBody | Out-Null
} else {
    $createBody = (@{ key = "VITE_API_BASE_URL" } + ($envBody | ConvertFrom-Json | ConvertTo-Json -Depth 5 | ConvertFrom-Json)) | ConvertTo-Json
    Invoke-RestMethod `
        -Uri "https://api.vercel.com/v9/projects/$VERCEL_PROJECT/env" `
        -Headers $headers -Method Post -Body $createBody | Out-Null
}
Write-Host "       ✓ VITE_API_BASE_URL = $tunnelUrl" -ForegroundColor Green

# ── Step 4: Trigger Vercel redeploy via empty git commit ─────────────────────
Write-Host "  [4/4] Triggering Vercel redeploy..." -ForegroundColor Green
try {
    Push-Location $Root
    git commit --allow-empty -m "chore(deploy): update backend tunnel URL [skip ci]" 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    Write-Host "       ✓ Vercel rebuild triggered (takes ~30 seconds)" -ForegroundColor Green
} catch {
    Write-Host "       [WARN] Could not push git commit. Trigger redeploy manually on Vercel." -ForegroundColor Yellow
} finally {
    Pop-Location
}

# ── Ready! ────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║              🎉  Ceravox is LIVE!               ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend : $DASHBOARD_URL" -ForegroundColor Cyan
Write-Host "  Backend  : $tunnelUrl" -ForegroundColor Cyan
Write-Host "  API docs : http://127.0.0.1:$BACKEND_PORT/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Vercel is rebuilding (~30 sec). After that, $DASHBOARD_URL" -ForegroundColor Yellow
Write-Host "  is fully live for all users worldwide." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Keep this window open while demoing. Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

# ── Keep alive ────────────────────────────────────────────────────────────────
try {
    while ($true) { Start-Sleep -Seconds 30 }
} finally {
    Write-Host "`n  Shutting down Ceravox..." -ForegroundColor Yellow
    if ($backendProcess -and -not $backendProcess.HasExited) {
        $backendProcess.Kill(); Write-Host "  ✓ Backend stopped." -ForegroundColor Gray
    }
    if ($tunnelProcess -and -not $tunnelProcess.HasExited) {
        $tunnelProcess.Kill(); Write-Host "  ✓ Tunnel closed." -ForegroundColor Gray
    }
    Write-Host "  Goodbye." -ForegroundColor Cyan
}
