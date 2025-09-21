@echo off
pyinstaller --noconsole --icon=icon.ico --add-data "icon.ico;." --clean --uac-admin --onefile main.py
pause