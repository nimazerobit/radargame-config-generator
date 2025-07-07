@echo off
cls
echo === Installing Python packages from requirements.txt ===

:: Try pip and pip3
where pip >nul 2>nul
if %errorlevel%==0 (
    set PIP_CMD=pip
) else (
    where pip3 >nul 2>nul
    if %errorlevel%==0 (
        set PIP_CMD=pip3
    ) else (
        echo [ERROR] Neither pip nor pip3 was found on your system.
        pause
        exit /b 1
    )
)

%PIP_CMD% install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install some packages.
    pause
    exit /b 1
)

echo [SUCCESS] All packages installed successfully.
pause
