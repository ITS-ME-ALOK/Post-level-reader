@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Building PDF To Excel Converter...
pyinstaller --noconfirm --name "Post level reader" --onefile --windowed main.py

echo Build complete! Check the 'dist' folder for your executable.
pause
