@echo off
setlocal enabledelayedexpansion

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
echo  PUBLISH QR
echo  TARGET : !SRC!
echo ==========================================
echo.

REM ── Safety check: must be a folder named QR ───────────────────────────────
for %%I in ("!SRC!") do set "FNAME=%%~nxI"
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

REM ── Paths ─────────────────────────────────────────────────────────────────
set "REPO_ROOT=X:\ASAP_MAIN\ENGINEERING\CUSTOMER\GITHUB REPO\SHOP LIBRARY\shop-library"
set "PY_PUBLISH=%REPO_ROOT%\publish_anywhere.py"

REM ── Check repo is reachable ───────────────────────────────────────────────
if not exist "%REPO_ROOT%" (
    echo ERROR: Cannot reach repo folder:
    echo        %REPO_ROOT%
    echo.
    echo  Is the X: drive connected?
    echo.
    goto :END
)

if not exist "%PY_PUBLISH%" (
    echo ERROR: Cannot find publish_anywhere.py at:
    echo        %PY_PUBLISH%
    echo.
    goto :END
)

REM ── Run Python DIRECTLY - no redirection so prompts appear here ───────────
echo --- RUNNING PUBLISH ---
echo  (Answer any y/n prompts below as they appear)
echo.

python "%PY_PUBLISH%" "!SRC!"
set "EXITCODE=%ERRORLEVEL%"

echo.
if %EXITCODE% NEQ 0 (
    echo ==========================================
    echo  PUBLISH FAILED  ^(exit code %EXITCODE%^)
    echo ==========================================
) else (
    echo ==========================================
    echo  PUBLISH COMPLETE
    echo ==========================================
)

:END
echo.
pause
endlocal
