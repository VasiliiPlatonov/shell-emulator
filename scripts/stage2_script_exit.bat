@echo off
rem Скрипт с exit: окно закроется само
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --script scripts\startup\exit.txt
