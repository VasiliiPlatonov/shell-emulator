@echo off
rem Этап 4: все режимы ls, cd, wc, cal на многоуровневой VFS
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --vfs vfs\deep.csv --log logs\stage4.xml --script scripts\startup\stage4.txt
