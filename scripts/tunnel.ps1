# Ceravox Quick Tunnel Helper
# Exposes the local dashboard & backend to an instant, secure public HTTPS URL using Cloudflare Tunnels (100% Free).

$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "       Ceravox Free Public Tunnel (Cloudflare)   " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure backend and dashboard are running
$backendCheck = try { (Invoke-WebRequest -Uri "http://127.0.0.1:8000/v1/auth/status" -UseBasicParsing -TimeoutSec 2).StatusCode } catch { 0 }
$dashboardCheck = try { (Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2).StatusCode } catch { 0 }

if ($backendCheck -ne 200 -or $dashboardCheck -ne 200) {
    Write-Host "[WARN] Make sure your Ceravox services are running before creating a tunnel." -ForegroundColor Yellow
    Write-Host "       Run: .\scripts\dev.ps1 or start backend & dashboard in another terminal." -ForegroundColor Yellow
    Write-Host ""
}

# Locate cloudflared binary
$cloudflaredCmd = Get-Command cloudflared -ErrorAction SilentlyContinue
$localBin = Join-Path $PSScriptRoot "cloudflared.exe"

if (-not $cloudflaredCmd -and -not (Test-Path $localBin)) {
    Write-Host "[INFO] 'cloudflared' not found. You can install it via:" -ForegroundColor Cyan
    Write-Host "       winget install Cloudflare.cloudflared" -ForegroundColor White
    Write-Host ""
    $reply = Read-Host "Would you like to download the official standalone executable from Cloudflare now? (Y/n)"
    if ($reply -eq "" -or $reply -match "^[Yy]") {
        Write-Host "Downloading cloudflared-windows-amd64.exe from Cloudflare GitHub releases..." -ForegroundColor Cyan
        $downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $localBin -UseBasicParsing
        Write-Host "Downloaded successfully to $localBin" -ForegroundColor Green
    } else {
        Write-Host "Exiting. Please install cloudflared and re-run this script." -ForegroundColor Yellow
        exit 1
    }
}

$binPath = if ($cloudflaredCmd) { $cloudflaredCmd.Source } else { $localBin }

Write-Host ""
Write-Host "[STARTING TUNNEL] Connecting http://127.0.0.1:5173 to Cloudflare..." -ForegroundColor Green
Write-Host "Look for the URL ending with '.trycloudflare.com' below." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to close the tunnel." -ForegroundColor Gray
Write-Host ""

& $binPath tunnel --url http://127.0.0.1:5173

