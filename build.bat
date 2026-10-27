@echo off
setlocal
cd /d "%~dp0"

echo === Instalacja zaleznosci ===
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo === Budowa ScreenOCR.exe ===
python -m PyInstaller --noconfirm --clean ^
  --name ScreenOCR ^
  --windowed ^
  --onefile ^
  --hidden-import winocr ^
  --hidden-import pystray._win32 ^
  --collect-all winocr ^
  run.py

if errorlevel 1 (
  echo Budowa nie powiodla sie.
  exit /b 1
)

echo.
echo Gotowe: dist\ScreenOCR.exe
echo Uruchom jako administrator tylko jesli skrot Ctrl+Shift+S nie dziala.
explorer dist
endlocal
