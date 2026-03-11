@echo off
setlocal

REM If dropped onto the bat, use that folder; otherwise current folder
if "%~1"=="" (
  set "SRC=%cd%"
) else (
  set "SRC=%~1"
)
REM Strip trailing backslash if present
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"

REM Safety: must be a folder named QR
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
set "PY_PUBLISH=%REPO_ROOT%\publish_anywhere.py"

echo ==========================================
echo PUBLISH QR (MANUAL STEP)
echo TARGET: %SRC%
echo PY: %PY_PUBLISH%
echo ==========================================

REM Hard fail if python file not found
if not exist "%PY_PUBLISH%" (
  echo.
  echo ERROR: Cannot find publish_anywhere.py here:
  echo %PY_PUBLISH%
  echo.
  pause
  exit /b 1
)

echo.
echo --- STEP CHECK (manual for now) ---
if exist "%SRC%\*.step" (
  echo STEP found in QR folder. Good.
) else (
  echo [WARN] No STEP found in QR folder.
  echo        (Manual STEP creation for now is OK.)
)

echo.
echo --- PUBLISH QR ---
echo --- Running Python ---
python "%PY_PUBLISH%" "%SRC%" >> "%TEMP%\publish_qr_log.txt" 2>&1
echo Python exit code: %ERRORLEVEL% >> "%TEMP%\publish_qr_log.txt"
type "%TEMP%\publish_qr_log.txt"
pause
```

Then try the Send To again. Even if it flashes, check this file:
```
C:\Users\[YourUsername]\AppData\Local\Temp\publish_qr_log.txt

pause
