@echo off
rem Справка по параметрам командной строки
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --help
pause
