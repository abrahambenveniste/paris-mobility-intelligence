@echo off
cd /d "%~dp0.."
python src/disruption_history.py
if errorlevel 1 pause
