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

APP_VERSION=$(python -c "import sys; sys.path.insert(0, 'src'); from qa_evidence import __version__; print(__version__)")
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $APP_VERSION" "dist/QA Evidence Builder.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $APP_VERSION" "dist/QA Evidence Builder.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :NSHumanReadableCopyright string Copyright © 2026 Guide Jir. All rights reserved." "dist/QA Evidence Builder.app/Contents/Info.plist" || true
python scripts/validate_release.py --check-assets --macos-app "dist/QA Evidence Builder.app"

echo
echo "Build complete:"
echo "dist/QA Evidence Builder.app"
