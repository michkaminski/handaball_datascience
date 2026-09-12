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

echo.
echo Uruchamianie Flaska (Ctrl+C konczy serwer)...
uv run flask --app pilka_reczna run

endlocal
