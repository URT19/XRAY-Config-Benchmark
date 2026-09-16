@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  CF Xray IP Benchmark - Setup (Windows)
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERR] Python not found in PATH.
  echo Install Python 3.9+ from https://www.python.org/downloads/
  echo Make sure "Add python.exe to PATH" is checked.
  pause
  exit /b 1
)

python --version
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
  echo [ERR] pip install failed.
  pause
  exit /b 1
)

echo.
echo [OK] Setup complete.
echo.
echo Next:
echo   1. Put share-links in links.txt
echo   2. Put CF IPs in cfip.txt
echo   3. Edit config.json if needed
echo   4. Run run.bat
echo.
pause
