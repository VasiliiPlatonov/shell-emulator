@echo off
rem Запуск без параметров: все значения по умолчанию
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py 
