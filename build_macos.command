#!/bin/bash
set -e

cd "$(dirname "$0")"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(not ((3, 10) <= sys.version_info[:2] < (3, 14)))'; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3.10-3.13 is required. PySide6 6.8.3 does not support Python 3.14."
    exit 1
fi

if [ ! -d ".venv" ]; then
    "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -c 'import sys; raise SystemExit(not ((3, 10) <= sys.version_info[:2] < (3, 14)))' || {
    echo "Existing .venv uses an unsupported Python. Recreate it with Python 3.10-3.13."
    exit 1
}
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

pyinstaller \
    --noconfirm \
    --windowed \
    --name "QA Evidence Builder" \
    --paths src \
    --icon assets/icons/qa-evidence-builder.icns \
    --add-data "assets/icons/png/icon-256.png:assets/icons/png" \
    --osx-bundle-identifier "com.guidejir.qaevidencebuilder" \
    run.py

python scripts/stamp_macos_bundle.py "dist/QA Evidence Builder.app"
codesign --force --deep --sign - "dist/QA Evidence Builder.app"
python scripts/validate_release.py --check-assets --macos-app "dist/QA Evidence Builder.app"

echo
echo "Build complete:"
echo "dist/QA Evidence Builder.app"
