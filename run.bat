@echo off
rem Запуск эмулятора оболочки (Windows)
chcp 65001 > nul
python "%~dp0src\main.py" %*
