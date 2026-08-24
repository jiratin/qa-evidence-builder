#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

pyinstaller \
    --noconfirm \
    --windowed \
    --name "QA Evidence Builder" \
    --paths src \
    run.py

echo
echo "Build complete:"
echo "dist/QA Evidence Builder.app"
