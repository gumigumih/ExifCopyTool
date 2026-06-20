@echo off
setlocal EnableExtensions

REM Move to this bat file folder safely
pushd "%~dp0"

echo [1/4] Install requirements
where python >nul 2>nul
if %ERRORLEVEL%==0 (
  set "PYTHON_CMD=python"
) else (
  where py >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py -3"
  ) else (
    echo Python was not found. Install Python only on this build PC, then run this file again.
    pause
    popd
    exit /b 1
  )
)

%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 goto :error
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [2/4] Clean old build files
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ExifCopyTool.spec del /q ExifCopyTool.spec

echo [3/4] Build ExifCopyTool.exe
%PYTHON_CMD% -m PyInstaller --noconsole --onefile --name ExifCopyTool exif_context_app.py
if errorlevel 1 goto :error

echo [4/4] Done
echo Created: %CD%\dist\ExifCopyTool.exe
pause
popd
exit /b 0

:error
echo.
echo Build failed.
echo Current folder: %CD%
pause
popd
exit /b 1
