@echo off
rem Несуществующий скрипт: ошибка в окне
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --script scripts\startup\missing.txt
