#!/usr/bin/env bash
# Uruchomienie na Linuxie (Ubuntu Server) - odpowiednik run.bat.
# Tworzy .venv, gdy go brak, i instaluje zależności tylko po zmianie pyproject.toml/uv.lock.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

if [ ! -f .env ]; then
    echo "Brak pliku .env - skopiuj .env.example do .env i uzupełnij." >&2
    exit 1
fi

if command -v uv >/dev/null 2>&1; then
    # uv sam tworzy .venv (z Pythonem 3.13) i pomija instalację, gdy wszystko jest aktualne.
    uv sync --frozen --no-dev
    PYTHON=.venv/bin/python
else
    PYTHON_SYS=""
    for kandydat in python3.13 python3; do
        if command -v "$kandydat" >/dev/null 2>&1 \
            && "$kandydat" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 13))'; then
            PYTHON_SYS="$kandydat"
            break
        fi
    done
    if [ -z "$PYTHON_SYS" ]; then
        echo "Wymagany Python 3.13. Najprościej zainstalować uv:" >&2
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
        exit 1
    fi

    if [ ! -x .venv/bin/python ]; then
        echo "Tworzę .venv ($PYTHON_SYS)..."
        "$PYTHON_SYS" -m venv .venv
    fi
    PYTHON=.venv/bin/python

    hash_teraz="$(sha256sum pyproject.toml | cut -d' ' -f1)"
    hash_zapisany="$(cat .venv/.deps-hash 2>/dev/null || true)"
    if [ "$hash_teraz" != "$hash_zapisany" ]; then
        echo "Instaluję zależności..."
        "$PYTHON" -m pip install --upgrade pip
        "$PYTHON" -m pip install -e .
        echo "$hash_teraz" > .venv/.deps-hash
    fi
fi

# PDF (WeasyPrint) wymaga Pango: sudo apt install libpango-1.0-0 libpangoft2-1.0-0
if ! ldconfig -p 2>/dev/null | grep -q 'libpango-1.0.so'; then
    echo "Uwaga: brak libpango - PDF nie zadziała (sudo apt install libpango-1.0-0 libpangoft2-1.0-0)." >&2
fi

PORT="$(grep -E '^HDS_PORT=' .env | tail -n1 | cut -d= -f2 | tr -d '\r[:space:]' || true)"
echo "ZPRP: http://$(hostname -I 2>/dev/null | awk '{print $1}'):${PORT:-5057}/administracja/"
exec "$PYTHON" app.py
