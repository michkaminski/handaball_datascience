@echo off
setlocal

cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo Brak polecenia "uv" w PATH. Zainstaluj uv: https://docs.astral.sh/uv/
    exit /b 1
)

echo Sprawdzanie srodowiska .venv i zaleznosci (uv sync)...
uv sync
if errorlevel 1 (
    echo Blad podczas "uv sync".
    exit /b 1
)

if not defined WEASYPRINT_DLL_DIRECTORIES if exist "C:\msys64\mingw64\bin\libpango-1.0-0.dll" set "WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin"
if defined WEASYPRINT_DLL_DIRECTORIES set "PATH=%WEASYPRINT_DLL_DIRECTORIES%;%PATH%"

echo.
echo Uruchamianie Flaska (Ctrl+C konczy serwer)...
uv run python -m flask --app "handball:create_app()" run --port 5057

endlocal
