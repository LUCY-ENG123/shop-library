@echo off
setlocal enabledelayedexpansion

REM ── Keep window open no matter what ───────────────────────────────────────
REM  (we will pause at the very end always)

REM ── Resolve source folder ─────────────────────────────────────────────────
if not "%~1"=="" (
    set "SRC=%~1"
) else (
    set "SRC=%cd%"
)

REM Strip trailing backslash if present
if "!SRC:~-1!"=="\" set "SRC=!SRC:~0,-1!"

echo.
echo ==========================================
echo  PUBLISH QR  --  Diagnostic Mode
echo ==========================================
echo  Received path : !SRC!
echo.

REM ── Safety check: must be a folder named QR ───────────────────────────────
for %%I in ("!SRC!") do set "FNAME=%%~nxI"
echo  Folder name   : !FNAME!
echo.

if /I not "!FNAME!"=="QR" (
    echo ERROR: Folder must be named "QR"
    echo        You passed: !SRC!
    echo.
    echo HOW TO USE:
    echo   Right-click your QR folder ^> Send To ^> PUBLISH_QR
    echo   OR drag the QR folder onto this BAT file
    echo.
    goto :END
)

REM ── Paths ──────────────────────────────────────────────────────────────────
REM  *** EDIT THIS LINE to match where publish_anywhere.py actually lives ***
set "REPO_ROOT=X:\ASAP_MAIN\ENGINEERING\CUSTOMER\GITHUB REPO\SHOP LIBRARY\shop-library"
set "PY_PUBLISH=%REPO_ROOT%\publish_anywhere.py"
set "LOG=%TEMP%\publish_qr_log.txt"

echo  Repo root     : %REPO_ROOT%
echo  Python script : %PY_PUBLISH%
echo.

REM ── Check X: drive is accessible ──────────────────────────────────────────
if not exist "%REPO_ROOT%" (
    echo ERROR: Cannot reach repo folder:
    echo        %REPO_ROOT%
    echo.
    echo  Possible causes:
    echo    1. The X: network drive is not connected
    echo    2. The path has changed - edit REPO_ROOT in this BAT file
    echo    3. VPN or server is down
    echo.
    goto :END
)

REM ── Verify publish script exists ──────────────────────────────────────────
if not exist "%PY_PUBLISH%" (
    echo ERROR: Cannot find publish_anywhere.py at:
    echo        %PY_PUBLISH%
    echo.
    goto :END
)

REM ── STEP check ────────────────────────────────────────────────────────────
echo --- STEP CHECK ---
if exist "!SRC!\*.step" (
    echo STEP file found. Good.
) else (
    echo [WARN] No STEP file found in QR folder.
)
echo.

REM ── Run Python publish ────────────────────────────────────────────────────
echo --- RUNNING PUBLISH ---
if exist "%LOG%" del "%LOG%"

python "%PY_PUBLISH%" "!SRC!" > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"

type "%LOG%"
echo.

if %EXITCODE% NEQ 0 (
    echo PUBLISH FAILED  ^(exit code %EXITCODE%^)
) else (
    echo PUBLISH COMPLETE.
)

:END
echo.
echo ==========================================
pause
endlocal
