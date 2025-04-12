@echo off
start "AC7SM" python ace_combat.py

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)