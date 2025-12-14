@echo off
REM ============================================
REM Script para iniciar la aplicación con Cloudflare Tunnel
REM ============================================

echo.
echo 🌊 Sistema de Alertas de Inundaciones - CDMX
echo ============================================
echo.

REM Obtener el directorio actual
setlocal enabledelayedexpansion

echo [1/2] Iniciando servidor Flask...
echo.

REM Iniciar Flask en background
start "Flask Server" cmd /k "cd /d %~dp0src && python Flask_Server.py"

timeout /t 3 /nobreak

echo.
echo [2/2] Iniciando Cloudflare Tunnel...
echo.

REM Nota: Asume que cloudflared está instalado en PATH
REM Si no, reemplaza 'cloudflared' con la ruta completa

cloudflared tunnel run sistema-inundaciones

echo.
echo ============================================
echo Para detener: Presiona Ctrl+C en ambas ventanas
echo ============================================
