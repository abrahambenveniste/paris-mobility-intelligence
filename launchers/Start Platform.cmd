@echo off
cd /d "%~dp0.."
python run_platform.py --with-predictions
if errorlevel 1 pause
