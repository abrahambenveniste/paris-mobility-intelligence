@echo off
cd /d "%~dp0.."
python src/collect.py
if errorlevel 1 pause
