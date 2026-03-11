@echo off
setlocal enabledelayedexpansion

REM ── Resolve source folder ──────────────────────────────────────────────────
REM When used via Send To, Windows passes the selected item as %1
REM When double-clicked, fall back to current directory
if not "%~1"=="" (
    set "SRC=%~1"
) else (
    set "SRC=%cd%"
)

REM Strip trailing backslash if present
if "!SRC:~-1!"=="\" set "SRC=!SRC:~0,-1!"

REM ── Safety check: must be a folder named QR ────────────────────────────────
for %%I in ("!SRC!") do set "FNAME=%%~nxI"
if /I not "!FNAME!"=="QR" (
    echo.
    echo ERROR: Must run on a folder named "QR"
    echo Selected: !SRC!
    echo.
    echo HOW TO USE:
    echo   Right-click your QR folder ^> Send To ^> PUBLISH_QR
    echo   OR drag the QR folder onto PUBLISH_QR.bat directly
    echo.
    pause
    exit /b 1
)

REM ── Paths ──────────────────────────────────────────────────────────────────
set "REPO_ROOT=X:\ASAP_MAIN\ENGINEERING\CUSTOMER\GITHUB REPO\SHOP LIBRARY\shop-library"
set "PY_PUBLISH=%REPO_ROOT%\publish_anywhere.py"
set "LOG=%TEMP%\publish_qr_log.txt"

echo ==========================================
echo  PUBLISH QR
echo  TARGET : !SRC!
echo  SCRIPT : %PY_PUBLISH%
echo ==========================================

REM ── Verify publish script exists ───────────────────────────────────────────
if not exist "%PY_PUBLISH%" (
    echo.
    echo ERROR: Cannot find publish_anywhere.py at:
    echo %PY_PUBLISH%
    echo.
    pause
    exit /b 1
)

REM ── STEP check ─────────────────────────────────────────────────────────────
echo.
echo --- STEP CHECK ---
if exist "!SRC!\*.step" (
    echo STEP file found in QR folder. Good.
) else (
    echo [WARN] No STEP file found in QR folder.
    echo        Manual STEP creation is OK for now.
)

REM ── Run Python publish ─────────────────────────────────────────────────────
echo.
echo --- RUNNING PUBLISH ---
echo Log: %LOG%
echo.

REM Clear old log
if exist "%LOG%" del "%LOG%"

python "%PY_PUBLISH%" "!SRC!" > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"

type "%LOG%"
echo.
echo --- Python exit code: %EXITCODE% ---

if %EXITCODE% NEQ 0 (
    echo.
    echo PUBLISH FAILED. See log above.
) else (
    echo.
    echo PUBLISH COMPLETE.
)

pause
endlocal
