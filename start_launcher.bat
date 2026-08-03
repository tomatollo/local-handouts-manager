@echo off
REM ============================================================
REM  Start the Local Handouts Manager launcher.
REM  Put this .bat in the project root, next to app.py and
REM  launcher.py.
REM ============================================================

REM Move into the script's folder (the project root).
cd /d "%~dp0"

REM Activate the virtual environment if present.
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [warning] .venv not found: using the system Python.
)

REM Start the GUI. "pythonw" runs it WITHOUT a black console window in the
REM background; if you would rather also see the console, replace it with
REM "python".
start "" pythonw launcher.py

REM Note: if pythonw is unavailable, use:
REM python launcher.py
