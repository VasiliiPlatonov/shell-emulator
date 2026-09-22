@echo off
rem VFS с вложенностью не менее 3 уровней
cd /d "%~dp0.."
chcp 65001 > nul
if not exist tmp mkdir tmp
copy /y vfs\deep.csv tmp\deep.csv > nul
python src\main.py --vfs tmp\deep.csv --log logs\stage3_deep.xml --script scripts\startup\stage3.txt
