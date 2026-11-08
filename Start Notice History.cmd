@echo off
cd /d "%~dp0"
python disruption_history.py
if errorlevel 1 pause
