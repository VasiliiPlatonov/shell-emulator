@echo off
rem Ошибки загрузки VFS: для каждого файла открывается окно с сообщением
cd /d "%~dp0.."
chcp 65001 > nul
for %%f in (no_parent bad_type bad_base64 no_header) do python src\main.py --vfs vfs\broken\%%f.csv
python src\main.py --vfs vfs\no_such_file.csv
