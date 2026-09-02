#Requires -RunAsAdministrator
Write-Host '=== AI Story Studio — Instalacion ===' -ForegroundColor Yellow

# Python 3.11
Write-Host ''
Write-Host '[1/7] Verificando Python 3.11...' -ForegroundColor Cyan
 $python = Get-Command python3.11 -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $v = & python --version 2>&1
        Write-Host "  Python encontrado: $v" -ForegroundColor Green
    } else {
        Write-Host '  Descargando Python 3.11...' -ForegroundColor Yellow
        Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile "$env:TEMP\python-installer.exe"
        Start-Process "$env:TEMP\python-installer.exe" -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
        $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
    }
}

# Node.js 20
Write-Host ''
Write-Host '[2/7] Verificando Node.js 20...' -ForegroundColor Cyan
 $node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host '  Descargando Node.js 20 LTS...' -ForegroundColor Yellow
    Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi' -OutFile "$env:TEMP\node-installer.msi"
    Start-Process msiexec.exe -ArgumentList "/i `"$env:TEMP\node-installer.msi`" /quiet" -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
}

# FFmpeg
Write-Host ''
Write-Host '[3/7] Verificando FFmpeg...' -ForegroundColor Cyan
 $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host '  Instalando FFmpeg via winget...' -ForegroundColor Yellow
    winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
}

# Backend venv
Write-Host ''
Write-Host '[4/7] Creando entorno virtual Python...' -ForegroundColor Cyan
Set-Location $PSScriptRoot\..
if (-not (Test-Path 'backend\.venv')) {
    python -m venv backend\.venv
}
& backend\.venv\Scripts\Activate.ps1
Write-Host '  Instalando dependencias Python...' -ForegroundColor Yellow
pip install --upgrade pip
pip install -r backend\requirements.txt

# Frontend
Write-Host ''
Write-Host '[5/7] Instalando dependencias Node.js...' -ForegroundColor Cyan
npm install

# ComfyUI
Write-Host ''
Write-Host '[6/7] Verificando ComfyUI...' -ForegroundColor Cyan
if (-not (Test-Path 'comfyui\ComfyUI')) {
    Write-Host '  Clonando ComfyUI...' -ForegroundColor Yellow
    git clone https://github.com/comfyanonymous/ComfyUI.git comfyui\ComfyUI
    Set-Location comfyui\ComfyUI
    pip install -r requirements.txt
    Set-Location $PSScriptRoot\..\..
}

# Redis
Write-Host ''
Write-Host '[7/7] Verificando Redis...' -ForegroundColor Cyan
 $redis = Get-Command redis-server -ErrorAction SilentlyContinue
if (-not $redis) {
    Write-Host '  Redis no encontrado. Usa Docker (docker compose up -d) o instala Memurai.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '=== Instalacion completada ===' -ForegroundColor Green
Write-Host 'Siguiente paso: python scripts\download_models.py --tier mvp' -ForegroundColor Cyan