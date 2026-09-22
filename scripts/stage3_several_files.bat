@echo off
rem VFS с несколькими файлами, включая двоичный (base64)
cd /d "%~dp0.."
chcp 65001 > nul
if not exist tmp mkdir tmp
copy /y vfs\several_files.csv tmp\several_files.csv > nul
python src\main.py --vfs tmp\several_files.csv --log logs\stage3_several_files.xml --script scripts\startup\stage3.txt
