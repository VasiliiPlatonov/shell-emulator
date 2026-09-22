@echo off
rem Минимальная VFS (только корень). VFS копируется в tmp, т.к. vfs-init её перезаписывает
cd /d "%~dp0.."
chcp 65001 > nul
if not exist tmp mkdir tmp
copy /y vfs\minimal.csv tmp\minimal.csv > nul
python src\main.py --vfs tmp\minimal.csv --log logs\stage3_minimal.xml --script scripts\startup\stage3.txt
