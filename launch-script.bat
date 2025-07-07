@echo off
cls
echo === Launching main.py ===

:: Try python and python3
where python >nul 2>nul
if %errorlevel%==0 (
    set PY_CMD=python
) else (
    where python3 >nul 2>nul
    if %errorlevel%==0 (
        set PY_CMD=python3
    ) else (
        echo [ERROR] Neither python nor python3 was found on your system.
        pause
        exit /b 1
    )
)

%PY_CMD% main.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run main.py
    pause
    exit /b 1
)
pause
