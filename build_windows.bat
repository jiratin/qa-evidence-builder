@echo off
setlocal

cd /d "%~dp0"

python -c "import sys; raise SystemExit(not ((3, 10) <= sys.version_info[:2] < (3, 14)))"
if errorlevel 1 (
    echo Python 3.10-3.13 is required. PySide6 6.8.3 does not support Python 3.14.
    exit /b 1
)

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate
python -c "import sys; raise SystemExit(not ((3, 10) <= sys.version_info[:2] < (3, 14)))"
if errorlevel 1 (
    echo Existing .venv uses an unsupported Python. Recreate it with Python 3.10-3.13.
    exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

pyinstaller --noconfirm --windowed --name "QA Evidence Builder" --paths src ^
  --icon assets\icons\qa-evidence-builder.ico ^
  --version-file packaging\windows_version_info.txt ^
  --add-data "assets\icons\png\icon-256.png:assets\icons\png" ^
  run.py

echo.
echo Build complete:
echo dist\QA Evidence Builder\QA Evidence Builder.exe
pause
