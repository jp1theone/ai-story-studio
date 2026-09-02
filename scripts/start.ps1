Write-Host "=== AI Story Studio — Iniciando ===" -ForegroundColor Yellow
 $root = $PSScriptRoot\..

# Redis
Write-Host "`n[1/4] Iniciando Redis..." -ForegroundColor Cyan
 $redisRunning = docker ps --filter "name=ai-studio-redis" --format "{{.Names}}"
if (-not $redisRunning) {
    docker start ai-studio-redis 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker compose -f "$root\docker-compose.yml" up -d
    }
}

# ComfyUI
Write-Host "[2/4] Iniciando ComfyUI..." -ForegroundColor Cyan
 $comfyProc = Start-Process -FilePath "python" -ArgumentList "$root\comfyui\ComfyUI\main.py","--listen","127.0.0.1","--port","8188" -WindowStyle Minimized -PassThru

# Backend
Write-Host "[3/4] Iniciando Backend (FastAPI)..." -ForegroundColor Cyan
& "$root\backend\.venv\Scripts\Activate.ps1"
 $apiProc = Start-Process -FilePath "python" -ArgumentList "-m","uvicorn","backend.main:app","--host","0.0.0.0","--port","8000","--reload" -WindowStyle Minimized -PassThru

# Frontend
Write-Host "[4/4] Iniciando Frontend (Vite)..." -ForegroundColor Cyan
 $feProc = Start-Process -FilePath "npx" -ArgumentList "vite","--host" -WindowStyle Minimized -PassThru

Write-Host "`n=== Todos los servicios iniciados ===" -ForegroundColor Green
Write-Host "  Estudio:    http://localhost:5173" -ForegroundColor White
Write-Host "  API:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  ComfyUI:    http://localhost:8188" -ForegroundColor White
Write-Host "`nPresiona Ctrl+C para detener todo." -ForegroundColor Gray