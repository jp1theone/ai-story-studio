# Arranque manual para diagnosticar AI Story Studio.
# Abre dos terminales: una muestra el backend y la otra el frontend.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

$python = Join-Path $projectDir "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "No se encontró el Python del entorno virtual: $python" -ForegroundColor Red
    exit 1
}

Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', "Set-Location '$projectDir'; & '$python' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', "Set-Location '$projectDir'; npm run dev"

Write-Host "Se abrieron dos terminales. Genera una historia y deja ambas abiertas." -ForegroundColor Green
Write-Host "El registro persistente queda en: $projectDir\logs\backend.log" -ForegroundColor Yellow
