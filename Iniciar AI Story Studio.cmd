@echo off
setlocal
cd /d "%~dp0"
title AI Story Studio
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 (
  echo.
  echo La aplicacion se cerro con un error. Revisa el mensaje anterior.
  pause
)
