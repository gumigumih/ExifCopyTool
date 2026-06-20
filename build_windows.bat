@echo off
setlocal
cd /d %~dp0
python -m pip install -r requirements.txt
python -m PyInstaller --noconsole --onefile --name ExifCopyTool exif_context_app.py
if exist exiftool.exe copy exiftool.exe dist\exiftool.exe
if exist "exiftool(-k).exe" copy "exiftool(-k).exe" "dist\exiftool(-k).exe"
echo.
echo Build finished. See dist\ExifCopyTool.exe
pause
