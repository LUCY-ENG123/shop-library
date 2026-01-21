@echo off
setlocal

REM === Determine source folder ===
if "%~1"=="" (
  set "SRC=%cd%"
) else (
  set "SRC=%~1"
)

REM === Safety: must be QR folder ===
for %%I in ("%SRC%") do set "FNAME=%%~nxI"
if /I not "%FNAME%"=="QR" (
  echo.
  echo ERROR: Must run on a folder named "QR"
  echo Selected: %SRC%
  pause
  exit /b 1
)

REM === Paths ===
set "REPO_ROOT=X:\ASAP_MAIN\ENGINEERING\CUSTOMER\GITHUB REPO\SHOP LIBRARY\shop-library"
set "PS_CONVERT=%REPO_ROOT%\convert_sw_to_step.ps1"
set "PY_PUBLISH=%REPO_ROOT%\publish_anywhere.py"

REM === Sanity checks ===
if not exist "%PS_CONVERT%" (
  echo.
  echo ERROR: Missing PowerShell converter:
  echo %PS_CONVERT%
  pause
  exit /b 1
)

if not exist "%PY_PUBLISH%" (
  echo.
  echo ERROR: Missing Python publisher:
  echo %PY_PUBLISH%
  pause
  exit /b 1
)

echo ==========================================
echo PUBLISH QR (ALL-IN-ONE)
echo TARGET: %SRC%
echo PS: %PS_CONVERT%
echo PY: %PY_PUBLISH%
echo ==========================================
echo.

echo ==============================
echo === STEP CONVERSION STAGE ===
echo ==============================
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_CONVERT%" "%SRC%"
echo.

echo ============================
echo === PUBLISH PYTHON STAGE ===
echo ============================
python "%PY_PUBLISH%" "%SRC%"
echo.

pause
