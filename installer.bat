@echo off
title BRIGHTOS — Infrastructure Deployment
echo 💠 BRIGHTOS Engine Installation...
echo --------------------------------------------------

:: Try 'py' launcher first
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=py
    goto :INSTALL
)

:: Try 'python' next
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto :INSTALL
)

echo ❌ ERROR: Python not detected.
pause
exit /b

:INSTALL
echo ✅ Engine: %PY_CMD%
%PY_CMD% -m pip install -r deps.txt
%PY_CMD% -m playwright install
echo --------------------------------------------------
echo ✅ READY. USE run.bat TO IGNITE.
timeout /t 3
