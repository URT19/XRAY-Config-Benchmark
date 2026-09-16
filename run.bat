@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  CF Xray IP Benchmark
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERR] Python not found. Run setup.bat first.
  pause
  exit /b 1
)

REM Kill leftover xray processes that may hold ports
taskkill /F /IM xray.exe >nul 2>&1

python cf_xray_benchmark.py %*
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% neq 0 (
  echo [ERR] Exit code %EXITCODE%
) else (
  echo [OK] Finished.
)
pause
exit /b %EXITCODE%
