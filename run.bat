@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo Brak polecenia "uv" w PATH. Zainstaluj uv: https://docs.astral.sh/uv/
    exit /b 1
)

uv sync
if errorlevel 1 exit /b 1

if not defined WEASYPRINT_DLL_DIRECTORIES if exist "C:\msys64\mingw64\bin\libpango-1.0-0.dll" set "WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin"
if defined WEASYPRINT_DLL_DIRECTORIES set "PATH=%WEASYPRINT_DLL_DIRECTORIES%;%PATH%"

echo ZPRP: http://127.0.0.1:5057/administracja/
uv run python app.py
endlocal
