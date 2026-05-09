@echo off
echo Building CoretDraw.exe...
pip install -r requirements.txt
pyinstaller --onefile --windowed --name CoretDraw main.py
echo Build selesai. File EXE ada di folder dist\CoretDraw.exe
pause
