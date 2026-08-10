@echo off
setlocal EnableExtensions EnableDelayedExpansion
REM ============================================================
REM  Local Handouts Manager - launcher (Windows)
REM
REM  Double-click this file to start the desktop launcher. On
REM  first run it checks the prerequisites and sets up what it
REM  needs (virtual environment + dependencies), so a fresh PC
REM  works with one double-click.
REM
REM  Keep this file in the project root, next to app.py and
REM  launcher.py.
REM ============================================================

title Local Handouts Manager - launcher

REM --- Work from this script's folder (the project root) ------------------
cd /d "%~dp0"

echo ============================================================
echo   Local Handouts Manager - launcher (Windows)
echo   %cd%
echo ============================================================
echo.

REM --- 1. Find a suitable Python (3.9+) -----------------------------------
REM Try the "python" command first, then the "py" launcher. We store the
REM working command in PYCMD. Each candidate is version-checked (>= 3.9).
set "PYCMD="

for %%C in ("python" "py -3") do (
    if not defined PYCMD (
        %%~C -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3,9) else 1)" >nul 2>&1
        if !errorlevel! equ 0 set "PYCMD=%%~C"
    )
)

if not defined PYCMD (
    echo [error] Python 3.9 or newer was not found on this PC.
    echo.
    echo     Install it from https://www.python.org/downloads/windows/
    echo     On the FIRST installer screen, tick "Add python.exe to PATH".
    echo     Then run this file again.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%V in ('%PYCMD% --version 2^>^&1') do set "PYVER=%%V"
echo [ok] Python found: !PYVER!

REM --- 2. Ensure the virtual environment exists --------------------------
set "FRESH_VENV=0"
if not exist ".venv\Scripts\python.exe" (
    echo [..] No virtual environment yet - creating .venv ^(first-time setup^)...
    %PYCMD% -m venv .venv
    if !errorlevel! neq 0 (
        echo [error] Could not create the virtual environment.
        pause
        exit /b 1
    )
    echo [ok] Created .venv
    set "FRESH_VENV=1"
)

set "VENV_PY=.venv\Scripts\python.exe"
set "VENV_PYW=.venv\Scripts\pythonw.exe"
if not exist "%VENV_PY%" (
    echo [error] The virtual environment looks broken ^(no %VENV_PY%^).
    echo     Delete the .venv folder and run this again to rebuild it.
    pause
    exit /b 1
)

REM --- 3. Ensure dependencies are installed ------------------------------
REM Cheap check: can the venv import the key packages? If not (fresh venv,
REM or a new dependency appeared on update), install from requirements.txt.
set "NEED_INSTALL=0"
if "!FRESH_VENV!"=="1" (
    set "NEED_INSTALL=1"
) else (
    "%VENV_PY%" -c "import importlib.util as u,sys; sys.exit(1 if any(u.find_spec(m) is None for m in ('flask','waitress','fitz','PIL')) else 0)" >nul 2>&1
    if !errorlevel! neq 0 set "NEED_INSTALL=1"
)

if "!NEED_INSTALL!"=="1" (
    echo [..] Installing dependencies ^(this can take a minute the first time^)...
    "%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
    "%VENV_PY%" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [error] Installing dependencies failed. See the messages above.
        pause
        exit /b 1
    )
    echo [ok] Dependencies installed
) else (
    echo [ok] Dependencies already present
)

REM --- 4. Launch the GUI -------------------------------------------------
REM Prefer pythonw.exe: it runs the GUI WITHOUT a black console window.
echo.
echo [ok] Starting the launcher...
if exist "%VENV_PYW%" (
    start "" "%VENV_PYW%" launcher.py
) else (
    start "" "%VENV_PY%" launcher.py
)

REM Give any early error a moment to surface, then close this window.
endlocal
exit /b 0
