@echo off
setlocal
cd /d %~dp0

echo [1/4] Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [2/4] Cleaning old build files...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q ExifCopyTool.spec 2>nul

echo [3/4] Building ExifCopyTool.exe...
python -m PyInstaller --noconsole --onefile --name ExifCopyTool exif_context_app.py

echo [4/4] Done.
echo dist\ExifCopyTool.exe を起動してください。
pause
