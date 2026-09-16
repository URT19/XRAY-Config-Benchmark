@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found. Run setup.bat first.
  pause
  exit /b 1
)
python gui.py
if errorlevel 1 pause
