@echo off
rem Этап 5: все режимы mv и touch; изменения только в памяти
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --vfs vfs\deep.csv --log logs\stage5.xml --script scripts\startup\stage5.txt
