# Script de inicio para AI Story Studio en Windows
# Ejecutar con: .\start.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       AI STORY STUDIO — Iniciando...         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─── Verificar dependencias ───────────────────────────────
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Yellow

# Python: el entorno virtual puede quedar apuntando a una versión que fue desinstalada.
# Se selecciona un intérprete que realmente pueda arrancar antes de iniciar servicios.
$pythonCmd = $null
$venvPython = Join-Path $scriptDir "backend\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    try {
        & $venvPython --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "& '$venvPython'" }
    } catch { }
}
if (-not $pythonCmd) {
    $installedPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
    if (Test-Path $installedPython) {
        try {
            & $installedPython --version 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $pythonCmd = "& '$installedPython'" }
        } catch { }
    }
}
if (-not $pythonCmd) {
    try {
        py -3.14 --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "py -3.14" }
    } catch { }
}
if (-not $pythonCmd) {
    try {
        python --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "python" }
    } catch { }
}

try {
    if (-not $pythonCmd) { throw "No se encontró un intérprete funcional" }
    $pyVersion = Invoke-Expression "$pythonCmd --version" 2>&1
    Write-Host "   ✅ $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python no encontrado. Instala Python 3.10+" -ForegroundColor Red
    exit 1
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Node.js no encontrado. Instala Node.js 18+" -ForegroundColor Red
    exit 1
}

# FFmpeg
try {
    $ffmpegOut = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "   ✅ FFmpeg disponible" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  FFmpeg no encontrado. Los videos no se ensamblarán." -ForegroundColor Yellow
    Write-Host "      Descárgalo en: https://ffmpeg.org/download.html" -ForegroundColor Yellow
}

# gTTS (para narración sin F5-TTS)
try {
    Invoke-Expression "$pythonCmd -c 'import gtts'" 2>&1 | Out-Null
    Write-Host "   ✅ gTTS disponible (narración online)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  gTTS no instalado. Instalando..." -ForegroundColor Yellow
    Set-Location $scriptDir
    Invoke-Expression "$pythonCmd -m pip install gtts --quiet"
    Write-Host "   ✅ gTTS instalado" -ForegroundColor Green
}

# Pillow (para imágenes placeholder)
try {
    Invoke-Expression "$pythonCmd -c 'import PIL'" 2>&1 | Out-Null
    Write-Host "   ✅ Pillow disponible (imágenes placeholder)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Pillow no instalado. Instalando..." -ForegroundColor Yellow
    Set-Location $scriptDir
    Invoke-Expression "$pythonCmd -m pip install Pillow --quiet"
    Write-Host "   ✅ Pillow instalado" -ForegroundColor Green
}

Write-Host ""

# ─── Resetear la DB si tiene esquema viejo ────────────────
$dbPath = Join-Path $scriptDir "ai_story_studio.db"
if (Test-Path $dbPath) {
    Write-Host "🗄️  Base de datos existente encontrada." -ForegroundColor Yellow
    Write-Host "   Se actualizará el esquema automáticamente al iniciar." -ForegroundColor Yellow
    Write-Host ""
}

# ─── Crear directorios necesarios ────────────────────────
$dirs = @("output", "models\llm", "models\tts", "comfyui\workflows")
foreach ($dir in $dirs) {
    $fullPath = Join-Path $scriptDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}

# ─── Instalar dependencias frontend si es necesario ──────
$nodeModules = Join-Path $scriptDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "📦 Instalando dependencias frontend..." -ForegroundColor Yellow
    Set-Location $scriptDir
    npm install --silent
    Write-Host "   ✅ Dependencias frontend instaladas" -ForegroundColor Green
    Write-Host ""
}

# ─── Función para matar procesos al salir ─────────────────
$backendJob = $null
$frontendJob = $null
$comfyJob = $null

function Cleanup {
    Write-Host ""
    Write-Host "🛑 Deteniendo servicios..." -ForegroundColor Yellow
    if ($backendJob) { Stop-Job $backendJob; Remove-Job $backendJob -Force }
    if ($frontendJob) { Stop-Job $frontendJob; Remove-Job $frontendJob -Force }
    if ($comfyJob) { Stop-Job $comfyJob; Remove-Job $comfyJob -Force }
    Write-Host "   ✅ Servicios detenidos." -ForegroundColor Green
}

# ─── Iniciar Backend ──────────────────────────────────────
Write-Host "🐍 Iniciando Backend (FastAPI)..." -ForegroundColor Cyan
Set-Location $scriptDir

$backendCmd = "$pythonCmd -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

$backendJob = Start-Job -ScriptBlock {
    param($dir, $cmd)
    Set-Location $dir
    Invoke-Expression $cmd
} -ArgumentList $scriptDir, $backendCmd

Write-Host "   ✅ Backend iniciando en http://localhost:8000" -ForegroundColor Green
Write-Host "   📚 Documentación API: http://localhost:8000/docs" -ForegroundColor Green

# ─── Iniciar ComfyUI (motor de imágenes reales) ──────────
$comfyPython = Join-Path $scriptDir "comfyui\ComfyUI\.venv\Scripts\python.exe"
$comfyMain = Join-Path $scriptDir "comfyui\ComfyUI\main.py"
$comfyWorkDir = Join-Path $scriptDir "comfyui\ComfyUI"
if ((Test-Path $comfyPython) -and (Test-Path $comfyMain)) {
    try {
        & $comfyPython -c "import torch; import sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>&1 | Out-Null
        $torchOk = $LASTEXITCODE -eq 0
        Write-Host "   GPU CUDA: $(if ($torchOk) { '✅ RTX 5050 detectada' } else { '⚠️  CPU mode' })" -ForegroundColor $(if ($torchOk) { 'Green' } else { 'Yellow' })
        Write-Host "🎨 Iniciando ComfyUI (motor visual Animagine XL)..." -ForegroundColor Cyan
        $comfyJob = Start-Job -ScriptBlock {
            param($workDir, $python, $main)
            Set-Location $workDir
            & $python $main --listen 127.0.0.1 --port 8188
        } -ArgumentList $comfyWorkDir, $comfyPython, $comfyMain
        Write-Host "   ✅ Motor visual iniciando en http://127.0.0.1:8188" -ForegroundColor Green
        Write-Host "   ℹ️  Carga inicial ~60s (modelos de 6 GB en VRAM)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Error iniciando ComfyUI: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ ComfyUI no encontrado. Rutas:" -ForegroundColor Red
    Write-Host "      Python: $comfyPython" -ForegroundColor Red
    Write-Host "      Main:   $comfyMain" -ForegroundColor Red
}


# Esperar a que FastAPI responda antes de levantar el frontend.
$backendReady = $false
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $backendReady) {
    Write-Host "   ⚠️  El backend no respondió a tiempo; revisa los mensajes [Backend]." -ForegroundColor Yellow
}

# ─── Iniciar Frontend ─────────────────────────────────────
Write-Host ""
Write-Host "⚛️  Iniciando Frontend (Vite)..." -ForegroundColor Cyan

$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList $scriptDir

Write-Host "   ✅ Frontend iniciando en http://localhost:5173" -ForegroundColor Green

# Esperar a que Vite escuche antes de abrir el navegador. Así se evita una
# pestaña con ERR_CONNECTION_REFUSED en equipos que arrancan más despacio.
$frontendReady = $false
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 5173)
        $tcp.Close()
        $frontendReady = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($frontendReady) {
    Start-Process "http://localhost:5173"
} else {
    Write-Host "   ⚠️  El frontend aún no respondió; abre http://localhost:5173 en unos segundos." -ForegroundColor Yellow
}

# ─── Mostrar URLs ─────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        AI STORY STUDIO — LISTO ✅            ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  🌐 App:      http://localhost:5173           ║" -ForegroundColor White
Write-Host "║  🔧 API:      http://localhost:8000           ║" -ForegroundColor White
Write-Host "║  📚 Docs:     http://localhost:8000/docs      ║" -ForegroundColor White
Write-Host "╠══════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Presiona Ctrl+C para detener todos          ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# ─── Mantener activo y mostrar logs ──────────────────────
try {
    while ($true) {
        # Mostrar logs del backend
        # Los errores de un job son registros normales: no deben detener el
        # lanzador ni matar el otro servicio.
        try { $backendLogs = Receive-Job $backendJob -ErrorAction SilentlyContinue 2>&1 } catch { $backendLogs = @($_) }
        if ($backendLogs) {
            $backendLogs | ForEach-Object {
                if ($_ -match "ERROR") { Write-Host "[Backend] $_" -ForegroundColor Red }
                elseif ($_ -match "WARNING") { Write-Host "[Backend] $_" -ForegroundColor Yellow }
                elseif ($_ -match "INFO") { Write-Host "[Backend] $_" -ForegroundColor Gray }
            }
        }

        # Mostrar logs del frontend
        try { $frontendLogs = Receive-Job $frontendJob -ErrorAction SilentlyContinue 2>&1 } catch { $frontendLogs = @($_) }
        if ($frontendLogs) {
            $frontendLogs | ForEach-Object {
                if ($_ -match "error") { Write-Host "[Frontend] $_" -ForegroundColor Red }
                elseif ($_ -match "warn") { Write-Host "[Frontend] $_" -ForegroundColor Yellow }
            }
        }

        # Mostrar errores del motor visual sin detener el backend ni el frontend.
        if ($comfyJob) {
            try { $comfyLogs = Receive-Job $comfyJob -ErrorAction SilentlyContinue 2>&1 } catch { $comfyLogs = @($_) }
            if ($comfyLogs) {
                $comfyLogs | ForEach-Object {
                    if ($_ -match "error|ERROR|Traceback") { Write-Host "[ComfyUI] $_" -ForegroundColor Red }
                    elseif ($_ -match "warning|WARNING") { Write-Host "[ComfyUI] $_" -ForegroundColor Yellow }
                    else { Write-Host "[ComfyUI] $_" -ForegroundColor DarkCyan }
                }
            }
        }

        Start-Sleep -Seconds 2
    }
} finally {
    Cleanup
}


