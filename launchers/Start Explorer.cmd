@echo off
cd /d "%~dp0.."
python src/app.py --open
if errorlevel 1 pause
