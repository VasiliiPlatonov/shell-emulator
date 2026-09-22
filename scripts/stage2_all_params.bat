@echo off
rem Все параметры: VFS, лог и стартовый скрипт (остановка на ошибке)
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --vfs vfs\deep.csv --log logs\stage2.xml --script scripts\startup\stage2.txt
