@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    py -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

pyinstaller --noconfirm --windowed --name "QA Evidence Builder" --paths src run.py

echo.
echo Build complete:
echo dist\QA Evidence Builder\QA Evidence Builder.exe
pause
