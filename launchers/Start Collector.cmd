@echo off
cd /d "%~dp0.."
python collect.py
if errorlevel 1 pause
